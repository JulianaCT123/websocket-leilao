from dataclasses import dataclass, field
from typing import Optional, Any, List, Dict

@dataclass(frozen=True)
class Item:
    """Representa um produto fixo que será leiloado."""
    id: int
    name: str
    image_url: str
    initial_bid: float

@dataclass(frozen=True)
class AuctionState:
    """A fotografia exata de tudo que está acontecendo na sala de leilão no momento."""
    
    # Status pode ser: "waiting" (esperando o Host iniciar), "running" (leilão acontecendo), "finished" (acabou)
    status: str = "waiting"

    # Criamos a lista fixa dos 3 itens que serão leiloados. 
    # Usamos o field(default_factory=...) para garantir que cada sala criada tenha sua própria lista.
    items: List[Item] = field(
        default_factory=lambda: [
            Item(id=1, name="Relógio de Luxo Vintage", image_url="https://via.placeholder.com/300?text=Relogio", initial_bid=500.0),
            Item(id=2, name="Carro Esportivo Clássico", image_url="https://via.placeholder.com/300?text=Carro", initial_bid=50000.0),
            Item(id=3, name="Quadro Renascentista", image_url="https://via.placeholder.com/300?text=Quadro", initial_bid=15000.0)
        ]
    )

    # Índice para saber qual item está sendo leiloado agora (0 = Relógio, 1 = Carro, 2 = Quadro)
    current_item_index: int = 0
    
    # Tempo regressivo
    time_remaining: int = 60

    # Informações do lance vencedor no momento
    highest_bid: float = 0.0
    highest_bidder: Optional[str] = None

    # Lista onde guardaremos os vencedores quando cada leilão acabar
    winners: List[Dict[str, Any]] = field(default_factory=list)

    # Lista com o nome dos clientes que entraram na sala
    players: List[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Transforma esse estado num formato que o JavaScript (frontend) consiga entender."""
        
        # Pega o item atual, se o índice ainda for válido (menor que 3)
        current_item = None
        if self.current_item_index < len(self.items):
            current_item = self.items[self.current_item_index]

        return {
            "status": self.status,
            "current_item": {
                "id": current_item.id,
                "name": current_item.name,
                "image_url": current_item.image_url,
                "initial_bid": current_item.initial_bid
            } if current_item else None,
            "time_remaining": self.time_remaining,
            "highest_bid": self.highest_bid,
            "highest_bidder": self.highest_bidder,
            "winners": self.winners,
            "players": self.players
        }