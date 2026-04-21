from dataclasses import replace
from game.entities import AuctionState

class AuctionLogic:
    def __init__(self) -> None:
        self._state = AuctionState()

    @property
    def state(self) -> AuctionState:
        return self._state

    def add_player(self, name: str) -> tuple[bool, str]:
        if self._state.status != "waiting":
            return False, "O leilão já começou ou já terminou."
        
        # Limite de 3 clientes para testes, como você pediu
        if len(self._state.players) >= 3:
            return False, "A sala já está cheia (limite de 3 clientes)."
            
        if name in self._state.players:
            return False, "Esse nome já está em uso na sala."

        # Cria uma nova lista de jogadores adicionando o novo nome
        new_players = self._state.players + [name]
        self._state = replace(self._state, players=new_players)
        return True, "Entrou com sucesso!"

    def start_auction(self) -> bool:
        if self._state.status == "waiting":
            self._state = replace(self._state, status="running", time_remaining=60)
            return True
        return False

    def process_bid(self, player_name: str, amount: float) -> tuple[bool, str]:
        if self._state.status != "running":
            return False, "O leilão não está aberto para lances no momento."
            
        current_item = self._state.items[self._state.current_item_index]
        
        if amount <= current_item.initial_bid:
            return False, f"O lance deve ser maior que o lance inicial (R$ {current_item.initial_bid})."
            
        if amount <= self._state.highest_bid:
            return False, f"O lance deve ser maior que o lance atual (R$ {self._state.highest_bid})."

        # Se passou pelas regras, atualiza o vencedor e o valor atual
        self._state = replace(self._state, highest_bid=amount, highest_bidder=player_name)
        return True, "Lance registrado com sucesso!"

    def tick(self) -> None:
        if self._state.status != "running":
            return

        new_time = self._state.time_remaining - 1

        if new_time > 0:
            # Apenas diminui o relógio
            self._state = replace(self._state, time_remaining=new_time)
        else:
            # O TEMPO ACABOU! Fazer a transição de item
            new_winners = list(self._state.winners)
            current_item = self._state.items[self._state.current_item_index]
            
            # Se alguém deu lance, salva nos vencedores
            if self._state.highest_bidder:
                new_winners.append({
                    "auction_number": self._state.current_item_index + 1,
                    "item_name": current_item.name,
                    "winner_name": self._state.highest_bidder,
                    "amount": self._state.highest_bid
                })
            
            next_index = self._state.current_item_index + 1
            
            if next_index >= len(self._state.items):
                # Acabaram os itens! Finaliza a sala
                self._state = replace(self._state, status="finished", time_remaining=0, winners=new_winners)
            else:
                # Passa para o próximo item, reseta o tempo e os lances
                self._state = replace(
                    self._state, 
                    current_item_index=next_index, 
                    time_remaining=60, 
                    highest_bid=0.0, 
                    highest_bidder=None,
                    winners=new_winners
                )