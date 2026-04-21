import json
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler
from tornado.ioloop import PeriodicCallback

from core.logger import get_logger
from server.manager import RoomManager

logger = get_logger("Handlers")

# O gerente único que cuida de todas as salas
room_manager = RoomManager()

class CreateRoomHandler(RequestHandler):
    """Lida com o clique no botão 'Criar Sala' da tela inicial"""
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "GET, OPTIONS")

    def options(self):
        self.set_status(204)
        self.finish()

    def get(self) -> None:
        room_id = room_manager.create_room()
        host = self.request.host
        # Criamos o link que será transformado em QR Code no frontend
        link = f"http://{host}/?sala={room_id}"
        logger.info(f"Nova sala de leilão criada: {room_id}")
        self.write({"room_id": room_id, "link": link})


class AuctionWebSocket(WebSocketHandler):
    """Gerencia a comunicação em tempo real de cada usuário"""
    _clients: list["AuctionWebSocket"] = []

    def check_origin(self, origin: str) -> bool:
        return True

    def open(self) -> None:
        # Adiciona o usuário na lista de conexões ativas
        AuctionWebSocket._clients.append(self)
        
        # Pega as informações da URL de conexão (ex: ws://...?sala=123&nome=Maria)
        self.room_id = self.get_argument("sala", None)
        self.is_host = self.get_argument("host", "false").lower() == "true"
        self.player_name = self.get_argument("nome", None)

        if not self.room_id:
            self._send_error("ID da Sala não fornecido.")
            return

        self.game = room_manager.get_room(self.room_id)
        if not self.game:
            self._send_error("Sala não encontrada ou leilão já encerrado!")
            return

        # Se quem está conectando for um Cliente, tenta colocar o nome dele na sala
        if not self.is_host:
            if not self.player_name:
                self._send_error("Nome do cliente não fornecido.")
                return
            sucesso, msg = self.game.add_player(self.player_name)
            if not sucesso:
                self._send_error(msg)  # Avisa que a sala tá cheia ou o nome já existe
                return

        # Confirma para o frontend que conectou com sucesso
        self.write_message(json.dumps({
            "type": "init", 
            "role": "host" if self.is_host else "client",
            "name": self.player_name
        }))
        
        # Avisa todo mundo da sala que alguém novo entrou
        self._broadcast_state()

    def on_message(self, message: str | bytes) -> None:
        if not hasattr(self, "game") or not self.game:
            return

        try:
            data = json.loads(message)
            action = data.get("action")

            # Se for o Host mandando iniciar o leilão
            if action == "start_auction" and self.is_host:
                if self.game.start_auction():
                    self._broadcast_state()
                    
            # Se for um Cliente dando um lance
            elif action == "bid" and not self.is_host:
                amount = float(data.get("amount", 0))
                sucesso, msg = self.game.process_bid(self.player_name, amount)
                
                if sucesso:
                    self._broadcast_state() # Lance válido: atualiza a tela de todos
                else:
                    # Lance inválido: manda o erro SÓ para quem tentou dar o lance
                    self.write_message(json.dumps({"type": "error", "message": msg}))

        except ValueError:
            self.write_message(json.dumps({"type": "error", "message": "Valor de lance inválido."}))
        except Exception as e:
            logger.error(f"Erro ao processar mensagem JSON: {e}")

    def on_close(self) -> None:
        if self in AuctionWebSocket._clients:
            AuctionWebSocket._clients.remove(self)

    def _send_error(self, message: str) -> None:
        self.write_message(json.dumps({"type": "error", "message": message}))
        self.close()

    def _broadcast_state(self) -> None:
        """Pega a 'fotografia' atual do leilão e manda para as telas"""
        payload = json.dumps({"type": "update", "state": self.game.state.to_dict()})
        for client in AuctionWebSocket._clients:
            if hasattr(client, "room_id") and client.room_id == self.room_id:
                client.write_message(payload)


# --- O RELÓGIO DO SERVIDOR ---
def game_ticker():
    """Função que roda a cada 1 segundo como um batimento cardíaco"""
    for room_id, logic in room_manager.rooms.items():
        if logic.state.status == "running":
            # Chama a função tick() que criamos no logic.py para diminuir o tempo
            logic.tick()
            
            # Pega o novo estado (com 1 segundo a menos) e empacota
            payload = json.dumps({"type": "update", "state": logic.state.to_dict()})
            
            # Manda a atualização do relógio para todos os clientes daquela sala
            for client in AuctionWebSocket._clients:
                if hasattr(client, "room_id") and client.room_id == room_id:
                    client.write_message(payload)

# Dizemos pro Tornado: "Rode a função game_ticker a cada 1000 milissegundos (1 segundo)"
PeriodicCallback(game_ticker, 1000).start()