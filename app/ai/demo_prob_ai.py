import numpy as np
import sqlalchemy as sa
from app import db
from app.models import Player
from app.ai.ai_interface import BaseAI

class DemoProbAI(BaseAI):
    """
    AI dùng phổ xác xuất để quyết định phát bắn
    """
    def __init__(self, game, name=None):
        super().__init__(game, name)
        self.prob_matrix = self.gen_prob_matrix()
        
    def place_ships(self):
        #Đặt tàu ngẫu nhiên
        self.auto_place_ships(self.name)
        
    def make_shot(self, attacker_name, target_name):
        #Lấy bảng thông tin của đối thủ
        board = self.get_board(target_name)
        if not board:
            self.log_action(f"Không tìm thấy bảng của {target_name}")
            return {"result": "invalid", "x": -1, "y": -1}
        
        #Tìm ô có xác xuất cao nhất trong phổ xác xuất
        best_val = -1e9
        best_x = best_y = -1
        for x in range(10):
            for y in range(10):
                if board[x][y] in (2, 3, 4):
                    self.prob_matrix[x][y] = 0
                    continue
                if self.prob_matrix[x][y] > best_val:
                    best_val = self.prob_matrix[x][y]
                    best_x, best_y = x, y

        x, y = best_x, best_y 
        self.log_action(f"Chọn ô ({x},{y}) có xác suất {best_val:.2f}")
        
        #Tạo phát bắn
        result_data = self.shoot(attacker_name, target_name, x, y)
        result_data.update({"x": x, "y": y})
        print(f"[DEBUG] {self.name} bắn vào ({x}, {y}) của {target_name}")
        db.session.commit()

        #Xử lí sau khi bắn 
        self.prob_matrix[x][y] = 0  #đã bắn
        if result_data['result'] == 'miss':
            self.log_action(f"Bắn hụt tại ({x},{y})")
            self.miss_update(x, y)
        elif result_data['result'] == 'hit':
            self.log_action(f"Bắn trúng tại ({x},{y})")
            self.hit_update(x, y)
        elif result_data['result'] == 'sunk':
            self.log_action(f"Đánh chìm tàu tại ({x},{y})")
            self.hit_update(x, y)
        
        #Mục đích để hiển thị trước khi emit log thôi
        max_val = max(max(row) for row in self.prob_matrix) or 1
        normalized = [[cell / max_val for cell in row] for row in self.prob_matrix]
        
        self.log_action(f"Cập nhật lại prob_matrix", 
                        prob_matrix = normalized)   #nhớ tolist() để json hóa được
        return result_data

        
               
    def gen_prob_matrix(self):
        """
        Tạo ma trận phổ xác xuất
        Ma trận này sẽ được tính bằng cách kiểm tra khả năng đặt tàu vào mỗi ô
        Cụ thể hơn là nếu có thể đặt tàu Carrier(5) theo chiều dọc vào ô (1,0)
        thì các ô (1,0), (2,0), (3,0), (4,0), (5,0) sẽ được cộng thêm 1
        """
        prob_matrix = np.zeros((10, 10), dtype=int)
        
        for lenght in self.ships.values():
            for orientation in ["H", "V"]:
                for x in range(10):
                    for y in range(10):
                        valid = True
                        cells = []
                        
                        for i in range(lenght):
                            nx = x + (i if orientation == "V" else 0)
                            ny = y + (i if orientation == "H" else 0)
                            if not self.in_bounds(nx, ny):
                                valid = False
                                break
                            cells.append((nx, ny))
                        if valid:
                            for (nx, ny) in cells:
                                prob_matrix[nx][ny] += 1
                            
        return prob_matrix
                        
    def miss_update(self, x, y):
        # Giảm nhẹ xác suất vùng lân cận
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if self.in_bounds(nx, ny):
                    self.prob_matrix[nx][ny] *= 0.8  # giảm 20%
                                        
    def hit_update(self, x, y):
        # Tăng xác suất cho các ô lân cận
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny):
                self.prob_matrix[nx][ny] *= 2.0  # tăng gấp đôi

        
        


  
