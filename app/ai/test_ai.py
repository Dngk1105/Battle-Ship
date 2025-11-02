import random
from app import db
from app.ai.ai_interface import BaseAI


class TestAI(BaseAI):
    """
    AI sinh ra để test, bắn ngẫu nhiên
    """

    def place_ships(self):
        print(f"[DEBUG] TestAI.place_ships() -> bắt đầu đặt tàu cho {self.name}")
        self.auto_place_ships(self.name)

    def make_shot(self, attacker_name, target_name):
        board = self.get_board(target_name)
        if not board:
            print(f"[ERROR] Không tìm thấy bảng của {target_name}")
            return {"result": "invalid", "x": -1, "y": -1}

        possible_moves = [(x, y) for x in range(10) for y in range(10)
                          if board[x][y] not in (2, 3, 4)]
        if not possible_moves:
            print("[DEBUG] AI không còn ô nào để bắn.")
            return {"result": "invalid", "x": -1, "y": -1}

        x, y = random.choice(possible_moves)
        print(f"[DEBUG] {self.name} bắn vào ({x}, {y}) của {target_name}")

        result_data = self.shoot(attacker_name, target_name, x, y)
        result_data.update({"x": x, "y": y})
        db.session.commit()

        return result_data
