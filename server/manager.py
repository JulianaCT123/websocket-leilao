import uuid
from game.logic import AuctionLogic

class RoomManager:
    def __init__(self) -> None:
        # Um dicionário que guarda todas as salas abertas.
        # Chave: ID da sala (ex: "a1b2c3d4")
        # Valor: A instância do AuctionLogic (o leiloeiro daquela sala)
        self.rooms: dict[str, AuctionLogic] = {}

    def create_room(self) -> str:
        # Gera um identificador único universal (UUID) e pega os primeiros 8 caracteres.
        room_id = str(uuid.uuid4())[:8]
        
        # Cria um novo leiloeiro (AuctionLogic) para esta sala específica.
        self.rooms[room_id] = AuctionLogic()
        
        return room_id

    def get_room(self, room_id: str) -> AuctionLogic | None:
        # Tenta encontrar a sala no dicionário. 
        # Se o ID não existir, o Python retorna 'None' (nada).
        return self.rooms.get(room_id)

    def delete_room(self, room_id: str) -> None:
        # Remove a sala do dicionário para liberar a memória do servidor 
        # quando o leilão acabar ou todos saírem.
        if room_id in self.rooms:
            del self.rooms[room_id]