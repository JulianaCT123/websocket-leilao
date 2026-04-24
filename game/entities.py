from dataclasses import dataclass, field
from typing import Optional, Any, List, Dict

@dataclass(frozen=True)
class Item:
    id: int
    name: str
    image_url: str
    initial_bid: float

@dataclass(frozen=True)
class AuctionState:    
    status: str = "waiting"

    items: List[Item] = field(
        default_factory=lambda: [
            Item(id=1, name="Carro de Luxo", image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkd1pYNCwd2zRwpn41yr3y3JRJFCMG8Oyj3Q&s", initial_bid=5.0),
            Item(id=2, name="A Lua", image_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSFKHPqv8wgWWV_3xg6v1gZFFd8QPkmLAhAEw&s", initial_bid=1000.0),
            Item(id=3, name="Quadro Renascentista", image_url="https://via.placeholder.com/300?text=Quadro", initial_bid=15000.0)
        ]
    )

    current_item_index: int = 0
    
    time_remaining: int = 30

    highest_bid: float = 0.0
    highest_bidder: Optional[str] = None

    winners: List[Dict[str, Any]] = field(default_factory=list)

    players: List[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        
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