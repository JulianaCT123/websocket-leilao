import uuid
from game.logic import AuctionLogic

class RoomManager:
    def __init__(self) -> None:
        self.rooms: dict[str, AuctionLogic] = {}

    def create_room(self) -> str:
        room_id = str(uuid.uuid4())[:8]
        
        self.rooms[room_id] = AuctionLogic()
        
        return room_id

    def get_room(self, room_id: str) -> AuctionLogic | None:
        return self.rooms.get(room_id)

    def delete_room(self, room_id: str) -> None:
        if room_id in self.rooms:
            del self.rooms[room_id]