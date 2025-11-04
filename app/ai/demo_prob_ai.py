import random
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
        self.init_matrix = self.init_prob_matrix() 

    
    def place_ships(self):
        #Đặt tàu ngẫu nhiên
        self.auto_place_ships(self.name)
        
    def make_shot(self, attacker_name, target_name):
        #Lấy bảng thông tin của đối thủ
        board = self.get_board(target_name)
        if not board:
            self.log_action(f"Không tìm thấy bảng của {target_name}")
            return {"result": "invalid", "x": -1, "y": -1}
        
        prob_matrix = self.calc_prob_matrix(board)
        # possible_moves = [(x, y) for x in range(10) for y in range(10)
        #                   if board[x][y] not in (2, 3, 4)]
        # x, y = random.choice(possible_moves)
        
        #Tìm ô có xác xuất cao nhất trong phổ xác xuất
        best_val = -1e9
        best_x = best_y = -1
        for x in range(10):
            for y in range(10):
                if board[x][y] in (2, 3, 4):
                    continue
                if prob_matrix[x][y] > best_val:
                    best_val = prob_matrix[x][y]
                    best_x, best_y = x, y

        x, y = best_x, best_y 
        self.log_action(f"Chọn ô ({x},{y}) có xác suất {best_val:.2f}")
        
        #Tạo phát bắn
        result_data = self.shoot(attacker_name, target_name, x, y)
        result_data.update({"x": x, "y": y})
        print(f"[DEBUG] {self.name} bắn vào ({x}, {y}) của {target_name}")
        db.session.commit()
        
        board = self.get_board(target_name)
        prob_matrix = self.calc_prob_matrix(board)
        self.log_action("Cập nhật prob_matrix", prob_matrix = prob_matrix.tolist())
        
        return result_data

        
               
    def init_prob_matrix(self):
        """
        Tạo ma trận phổ xác xuất ban đầu
        Ma trận này sẽ được tính bằng cách kiểm tra khả năng đặt tàu vào mỗi ô
        Cụ thể hơn là nếu có thể đặt tàu Carrier(5) theo chiều dọc vào ô (1,0)
        thì các ô (1,0), (2,0), (3,0), (4,0), (5,0) sẽ được cộng thêm 1
        """
        prob_matrix = np.zeros((10, 10), dtype=float)
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
    
    def calc_prob_matrix(self, board):
        prob_matrix = np.copy(self.init_matrix)
        for x in range(10):
            for y in range(10):
                if board[x][y] == 3:
                    prob_matrix = self.miss_update(prob_matrix, x, y)
                elif board[x][y] == 2:
                    prob_matrix = self.hit_update(prob_matrix, x, y)
                elif board[x][y] == 4:
                    prob_matrix = self.sunk_update(prob_matrix, self.game.player.playername, x, y)
        return prob_matrix
                
                        
    def miss_update(self, prob_matrix, x, y,):
        # Giảm nhẹ xác suất vùng lân cận
        m = prob_matrix
        m[x][y] = -1
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny):
                m[nx][ny] = np.round(m[nx][ny] * 0.8, 1)
                    
        return m
                                        
    def hit_update(self, prob_matrix, x, y):
        # Tăng xác suất cho các ô lân cận
        m = prob_matrix
        m[x][y] = 0
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny):
                m[nx][ny] = np.round(m[nx][ny] * 1.5, 1)
                
        return m
    
    def sunk_update(self, prob_matrix, target_name, x, y):
        prob_matrix[x][y] = 0
        getShip = self._get_ship_component(target_name, x, y)
        ship_name, comps = getShip
        for x, y in comps:
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if self.in_bounds(nx, ny) and (x, y) not in comps:
                    prob_matrix[nx][ny] = np.round(prob_matrix[nx][ny] * 0.8, 1)
        
        return prob_matrix


  
