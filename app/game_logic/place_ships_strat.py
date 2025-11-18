# place_ships_strat.py
import random
from app import db
from app.game_logic.base_logic import GameLogic   

class ShipPlacementStrategy(GameLogic):

    def strategy_random(self, board, ship_name, length, owner):
        """Random"""
        placed = False
        while not placed:
            orientation = random.choice(["H", "V"])
            x = random.randint(0, 9)
            y = random.randint(0, 9)
            if self.can_place(board, x, y, length, orientation):
                board = self.place_ship(board, x, y, length, orientation, ship_name, owner)
                placed = True
        return board

    
    def strategy_edge(self, board, ship_name, length, owner):
        """Đặt tàu sát mép bảng (nhưng tránh góc)."""
        edges = [
            (0, random.randint(1, 8)),        # mép trên
            (9, random.randint(1, 8)),        # mép dưới
            (random.randint(1, 8), 0),        # mép trái
            (random.randint(1, 8), 9),        # mép phải
        ]

        random.shuffle(edges)
        for x, y in edges:
            for orientation in ["H", "V"]:
                if self.can_place(board, x, y, length, orientation):
                    return self.place_ship(board, x, y, length, orientation, ship_name, owner)

        return self.strategy_random(board, ship_name, length, owner)


    def strategy_no_corners(self, board, ship_name, length, owner):
        """Tránh 4 góc"""
        for _ in range(40):
            x = random.randint(1, 8)
            y = random.randint(1, 8)
            orientation = random.choice(["H", "V"])
            if self.can_place(board, x, y, length, orientation):
                return self.place_ship(board, x, y, length, orientation, ship_name, owner)

        return self.strategy_random(board, ship_name, length, owner)

   
    def strategy_spread(self, board, ship_name, length, owner):
        """Giữ khoảng cách giữa các tàu."""
        for _ in range(50):
            x = random.randint(0, 9)
            y = random.randint(0, 9)
            orientation = random.choice(["H", "V"])

            if not self.can_place(board, x, y, length, orientation):
                continue

            # kiểm tra khoảng cách an toàn 1 ô
            safe = True
            for dx in range(-1, length+1):
                for dy in [-1, 0, 1]:
                    nx = x + dx if orientation == "V" else x + dy
                    ny = y + dx if orientation == "H" else y + dy

                    if self.in_bounds(nx, ny):
                        if board[nx][ny] == 1:
                            safe = False
                            break
                if not safe:
                    break

            if safe:
                return self.place_ship(board, x, y, length, orientation, ship_name, owner)

        return self.strategy_random(board, ship_name, length, owner)

 
    def strategy_cluster(self, board, ship_name, length, owner):
        """Đặt gần nhau để đánh lừa đối thủ."""
        for _ in range(50):
            x = random.randint(2, 7)
            y = random.randint(2, 7)
            orientation = random.choice(["H", "V"])

            if self.can_place(board, x, y, length, orientation):
                return self.place_ship(board, x, y, length, orientation, ship_name, owner)

        return self.strategy_random(board, ship_name, length, owner)


    def strategy_checkerboard_avoid(self, board, ship_name, length, owner):
        """Tránh đặt theo ô caro"""
        for _ in range(50):
            x = random.randint(0, 9)
            y = random.randint(0, 9)

            if (x + y) % 2 == 0:  # bỏ qua ô caro
                continue

            orientation = random.choice(["H", "V"])
            if self.can_place(board, x, y, length, orientation):
                return self.place_ship(board, x, y, length, orientation, ship_name, owner)

        return self.strategy_random(board, ship_name, length, owner)

   
   
   
   
   
   
    def auto_place_ships_strategy(self, owner_name, strategy="random"):
        board = self.init_board(owner_name)

        strat_map = {
            "random": self.strategy_random,
            "edge": self.strategy_edge,
            "nocorner": self.strategy_no_corners,
            "spread": self.strategy_spread,
            "cluster": self.strategy_cluster,
            "checker_avoid": self.strategy_checkerboard_avoid,
        }

        strat_func = strat_map.get(strategy, self.strategy_random)

        for ship_name, length in self.ships.items():
            board = strat_func(board, ship_name, length, owner_name)

        self.save_board(owner_name, board)
        return board
