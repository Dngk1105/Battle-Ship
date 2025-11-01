import json
from app import db, socketio
from app.models import ShipPlacement, Player
import sqlalchemy as sa
import random
from abc import ABC, abstractmethod
from app.game_logic.base_logic import GameLogic


#---------------Trừu tượng~------------------------- Hiện tại không quan trọng lắm!

class AIInterface(ABC):
    """
    Interface quy định mọi AI phải có 2 hàm chính:
    - place_ships(): cách AI đặt tàu
    - make_shot(): cách AI chọn ô để bắn
    """

    @abstractmethod
    def place_ships(self):
        pass

    @abstractmethod
    def make_shot(self, opponent_name):
        pass

class BaseAI(GameLogic, AIInterface):
    """
    Base class cho tất cả AI.
    Kế thừa toàn bộ logic của GameLogic,
    đồng thời buộc các lớp con phải định nghĩa cách đặt tàu và bắn.
    """
    
    def __init__(self, game, name=None):
        super().__init__(game)
        self.game = game
        self.name = name or (game.ai.name if game.ai else "AI bot")
            
        
    def place_ships(self):
        raise NotImplementedError
    
    def make_shot(self, attacker_name, target_name):
        raise NotImplementedError
    

#---------------------------------------AI chính-----------------------------------------------------

class TestAI(BaseAI):
    """
    AI Này sinh ra là để test
    Chọn nước bắn ngẫu nhiên thôi
    """
    def place_ships(self):
        print(f"[DEBUG] TestAI.place_ships() -> bắt đầu đặt tàu cho {self.name}")
        self.auto_place_ships(self.name)

    def make_shot(self, attacker_name, target_name):
        board = self.get_board(target_name)
        if not board:
            print(f"[ERROR] Không tìm thấy bảng của {target_name}")
            return {"result": "invalid", "x": -1, "y": -1}


        # Chọn ô ngẫu nhiên chưa bắn
        possible_moves = [(x, y) for x in range(10) for y in range(10)
                          if board[x][y] not in (2, 3, 4)]
        if not possible_moves:
            print("[DEBUG] AI không còn ô nào để bắn.")
            return {"result": "invalid", "x": -1, "y": -1}

        x, y = random.choice(possible_moves)
        print(f"[DEBUG] {self.name} bắn vào ({x}, {y}) của {target_name}")

        result_data = self.shoot(attacker_name, target_name, x, y)
        result_data['x'] = x
        result_data['y'] = y
        db.session.commit()
        
        return result_data





# ----------------------------------- Linh tinh -------------------------------------

def get_ai_instance(game):
    """
    Tạo instance AI dựa theo game.ai.name -> cần khớp tên class và tên của AI 
    """
    ai_name = getattr(game.ai, "name", None)
    if not ai_name:
        raise ValueError("game.ai.name chưa được thiết lập!")

    # Tìm class AI trong module hiện tại
    cls = globals().get(ai_name)
    if cls is None:
        raise ValueError(f"Không tìm thấy lớp AI có tên: {ai_name}")
    if not issubclass(cls, BaseAI):
        raise TypeError(f"{ai_name} không kế thừa BaseAI!")

    return cls(game)