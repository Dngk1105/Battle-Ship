import numpy
import random
from app import db
from app.models import Player, ShipPlacement
from app.ai.ai_interface import BaseAI

class ProbAI(BaseAI):
    """
    AI dùng phổ mật độ xác xuất để quyết định phát bắn
    Phổ dựa trên số lượng cấu hình có thể đặt được ở một ô
    """
    
    def __init__(self, game, name = None):
        super().__init__(game, name)
            
    def place_ships(self):
        """ Ưu tiên đặt ở góc (Tránh các ô ở giữa) """
        board = self.init_board(self.name)
        for ship_name, lenght in self.ships.items():
            placed = False
            while not placed:
                attempts += 1
                orientation = random.choice(["H", "V"])
                x = random.randint(0, 9)
                y = random.randint(0, 9)
                if self.can_place_avoid_center(board, x, y, lenght, orientation):
                    board = self.place_ship(board, x, y, lenght, orientation, ship_name, self.name)
                    placed = True
            self.save_board(self.name, board)
        return board
    
    def make_shot(self, attacker_name, target_name):
        board = self.get_board(target_name)
        if not board:
            self.log_action(f"Không tìm thấy bảng của {target_name}")
            return {"result": "invalid", "x": -1, "y": -1}
        
        ships_alive = self.get_ships_alive(target_name)
        
        
    

    def get_ships_alive(self, owner_name):
        """
        Lấy danh sách các tàu còn sống, chiều dài giảm dần
        """
        placement = db.session.scalar(
            db.select(ShipPlacement)
            .where(ShipPlacement.game_id == self.game.id)
            .where(ShipPlacement.owner == owner_name)
        )
        


