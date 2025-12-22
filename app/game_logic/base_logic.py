import json
from app import db
from app.models import ShipPlacement, Player
import sqlalchemy as sa
import random

# 0: ô trống
# 1: ô có tàu
# 2: bắn trúng
# 3: bắng trượt 
# 4: chìm

class GameLogic:
    """
    Lớp xử lý toàn bộ logic của trò chơi Battleship.
    """

    def __init__(self, game):
        self.game = game

        # Định nghĩa độ dài tàu
        self.ships = {
            "Carrier": 5,
            "Battleship": 4,
            "Cruiser": 3,
            "Submarine": 3,
            "Destroyer": 2,
        }

        # Lưu vị trí từng tàu (cho cả 2 bên)
        # { "player": { "Carrier": [(x1,y1), (x2,y2)...], ... }, "opponent": {...} }
        self.ship_positions = {
            self.game.player.playername: {},
            (self.game.opponent.playername if self.game.opponent else self.game.ai.name): {}
        }

    # --------------------------- Qlí bảng ---------------------------

    def init_board(self, owner_name, size=10):
        """Tạo ma trận trống cho người chơi, nếu chưa có thì khởi tạo."""
        empty_board = [[0 for _ in range(size)] for _ in range(size)]

        # Kiểm tra xem đã có record cho người chơi này trong game chưa
        placement = db.session.scalar(
            db.select(ShipPlacement)
            .where(ShipPlacement.game_id == self.game.id)
            .where(ShipPlacement.owner == owner_name)
        )

        if placement:
            # Nếu đã tồn tại thì chỉ cập nhật lại grid_data (reset bảng)
            placement.grid_data = json.dumps(empty_board)
            if placement.ship_data is None:
                placement.ship_data = json.dumps({})
        else:
            # Nếu chưa có thì tạo mới
            placement = ShipPlacement(
                game_id=self.game.id,
                owner=owner_name,
                grid_data=json.dumps(empty_board),
                ship_data=json.dumps({})  # đảm bảo không bị None
            )
            db.session.add(placement)

        db.session.commit()
        print(f"[DEBUG] init_board() -> Đảm bảo chỉ có 1 ShipPlacement cho {owner_name}")
        return empty_board


    def get_board(self, owner_name):
        """Lấy ma trận từ database"""
        placement = db.session.scalar(
            db.select(ShipPlacement)
            .where(ShipPlacement.game_id == self.game.id)
            .where(ShipPlacement.owner == owner_name)
        )
        if not placement:
            return None
        return json.loads(placement.grid_data)

    def save_board(self, owner_name, board):
        """Cập nhật ma trận của người chơi"""
        placement = db.session.scalar(
            db.select(ShipPlacement)
            .where(ShipPlacement.game_id == self.game.id)
            .where(ShipPlacement.owner == owner_name)
        )

        if placement:
            placement.grid_data = json.dumps(board)
        else:
            placement = ShipPlacement(
                game_id=self.game.id,
                owner=owner_name,
                grid_data=json.dumps(board),
            )
            db.session.add(placement)

        db.session.commit()

    # --------------------------- CORE LOGIC ---------------------------

    def in_bounds(self, x, y, size=10):
        """Kiểm tra toạ độ nằm trong bảng"""
        return 0 <= x < size and 0 <= y < size

    def can_place(self, board, x, y, length, orientation):
        """Kiểm tra xem có thể đặt tàu tại vị trí (x, y) không
            - Không vượt biên
            - Không đè tàu khác
            - Không chạm tàu khác (kể cả chéo)  // tạm thời bỏ 
        """
        for i in range(length):
            nx = x + (i if orientation == "V" else 0)
            ny = y + (i if orientation == "H" else 0)
            
            if not self.in_bounds(nx, ny):
                return False
            
            if board[nx][ny] != 0:
                return False
            
            # for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            #     adjx, adjy = nx + dx, ny + dy
            #     if not (0 <= adjx < len(board) and 0 <= adjy < len(board[0])):
            #         continue
            #     if board[adjx][adjy] == 1:
            #         return False
                
        return True

    def place_ship(self, board, x, y, length, orientation, ship_name, owner):
        """Đặt tàu lên bảng và lưu vị trí"""

        # Kiểm tra nếu tàu này đã được đặt
        if ship_name in self.ship_positions[owner]:
            return None

        # Kiểm tra vị trí có thể đặt được không
        if not self.can_place(board, x, y, length, orientation):
            return None

        # Đặt tàu
        positions = []
        for i in range(length):
            nx = x + (i if orientation == "V" else 0)
            ny = y + (i if orientation == "H" else 0)
            board[nx][ny] = 1
            positions.append((nx, ny))

        self.ship_positions[owner][ship_name] = positions
        # Lưu vào ShipPlacement.ship_data
        placement = db.session.scalar(
            db.select(ShipPlacement)
            .where(ShipPlacement.game_id == self.game.id)
            .where(ShipPlacement.owner == owner)
        )
        # nếu ship_data đã tồn tại thì cập nhật, chưa thì tạo mới
        if placement:
            data = json.loads(placement.ship_data or "{}")
            data[ship_name] = {
                "positions": positions,
                "sunked": False
            }
            placement.ship_data = json.dumps(data)
            placement.grid_data = json.dumps(board)
        else:
            placement = ShipPlacement(
                game_id=self.game.id,
                owner=owner,
                grid_data=json.dumps(board),
                ship_data=json.dumps({
                    ship_name: {"positions": positions, "sunked": False} 
                }),
            )
            db.session.add(placement)

        db.session.commit()
        print(f"[DEBUG] Cập nhật ship_data cho owner={owner}")
        try:
            current_data = json.loads(placement.ship_data or "{}")
            for name, info in current_data.items():
                pos = info.get("positions", [])
                sunk = info.get("sunked", False)
                print(f"  └─ {name}: {len(pos)} ô, sunked={sunk}, positions={pos}")
        except Exception as e:
            print(f"[DEBUG] Lỗi khi in ship_data của {owner}: {e}")
        return board
    
    def auto_place_ships(self, owner_name): 
        """Tự động đặt tàu ngẫu nhiên"""
        board = self.init_board(owner_name) 
        for ship_name, length in self.ships.items(): 
            placed = False 
            while not placed: 
                orientation = random.choice(["H", "V"]) 
                x = random.randint(0, 9) 
                y = random.randint(0, 9) 
                if self.can_place(board, x, y, length, orientation): 
                    board = self.place_ship(board, x, y, length, orientation, ship_name, owner_name) 				
                    placed = True 
        self.save_board(owner_name, board) 
        print(f"[DEBUG] auto_place_ships() -> Đặt bảng xong rùi đó {owner_name}")
        return board

    # --------------------------- SHOOTING LOGIC ---------------------------

    # kiểm tra phát bắn (tọa độ x, y)
    def shoot(self, attacker_name, target_name, x, y):
        """
        Xử lý phát bắn giữa 2 người (attacker → target)
        Trả về: {"result": "hit/miss/sunk/already_hit/out_of_bounds", "winner": optional_name}
        """
        print(f"[DEBUG] {attacker_name} bắn ({x},{y}) vào {target_name}")

        board = self.get_board(target_name)
        if not board:
            print(f"[DEBUG] Không tìm thấy bảng của {target_name}")
            return {"result": "invalid", "winner": None}

        # Kiểm tra toạ độ hợp lệ
        if not self.in_bounds(x, y):
            print(f"[DEBUG] Toạ độ ({x},{y}) ngoài phạm vi bảng!")
            return {"result": "out_of_bounds", "winner": None}

        cell = board[x][y]
        print(f"[DEBUG] Trạng thái ô ({x},{y}) trước khi bắn: {cell}")
        result = None

        # --- Xử lý các trường hợp ---
        if cell == 0:
            board[x][y] = 3
            result = "miss"
            print(f"[DEBUG] Bắn trượt ({x},{y})")

        elif cell == 1:
            board[x][y] = 2
            print(f"[DEBUG] Bắn trúng tàu tại ({x},{y})")
            ship_name, comp = self._get_ship_component(target_name, x, y)
            print(f"[DEBUG] Component tàu {ship_name} gồm {len(comp)} ô: {comp}")
            
            if comp and self._is_component_sunk(comp, board):
                self._mark_component_sunk(comp, board)
                result = "sunk"
                print(f"[DEBUG] Toàn bộ tàu đã chìm! Đánh dấu ô: {comp}")
                
                sunked_ship = ship_name
                if sunked_ship:
                    self._record_ship_sunk(target_name, sunked_ship)

            else:
                result = "hit"
                print(f"[DEBUG] Tàu chưa chìm hoàn toàn.")

        elif cell in (2, 3, 4):
            result = "already_hit"
            print(f"[DEBUG] Ô ({x},{y}) đã bị bắn trước đó.")

        # --- Lưu lại thay đổi ---
        self.save_board(target_name, board)
        print(f"[DEBUG] Đã lưu trạng thái mới của bảng {target_name}")

        # --- Cập nhật thống kê ---
        if attacker_name == getattr(self.game.player, "playername", None):
            self.game.player_shots += 1
            print(f"[DEBUG] +1 lượt bắn cho player {attacker_name}")
        elif attacker_name == getattr(self.game.opponent, "playername", None):
            self.game.opponent_shots += 1
            print(f"[DEBUG] +1 lượt bắn cho opponent {attacker_name}")
        elif attacker_name == getattr(self.game.ai, "name", None):
            self.game.opponent_shots += 1
            print(f"[DEBUG] +1 lượt bắn cho AI {attacker_name}")

        db.session.commit()

        # --- Kiểm tra thắng cuộc ---
        if self._all_ships_sunk(board):
            print(f"[DEBUG] {target_name} không còn tàu nào → {attacker_name} thắng trận!")
            self.game.status = "finished"
            self.game.winner = attacker_name
            
            player_win = db.session.scalar(
                sa.select(Player).where(Player.playername == attacker_name)
            )
            player_lose = db.session.scalar(
                sa.select(Player).where(Player.playername == target_name)
            )
            
            if player_win:
                player_win.wins = (player_win.wins or 0) + 1
            else:
                print(f"[ERROR] Không tìm thấy người thắng '{attacker_name}' trong bảng Player!")

            if player_lose:
                player_lose.losses = (player_lose.losses or 0) + 1
            else:
                print(f"[ERROR] Không tìm thấy người thua '{attacker_name}' trong bảng Player!")
            db.session.commit()
            print(f"[DEBUG]  Đã commit cập nhật kết quả thắng/thua vào DB.")
            
            return {
                "result": result, 
                "winner": attacker_name, 
                "owner": target_name, 
                "ship_name": ship_name, 
                "comp": comp,
                "x": x,
                "y": y
            }

        print(f"[DEBUG] Kết quả phát bắn: {result}")
        if result == 'sunk':
            return {
                "result": result,
                "winner": None,
                "owner": target_name,
                "ship_name": ship_name,
                "comp": comp,
                "x": x,
                "y": y
            }
        else: 
            return {
                "result": result, 
                "winner": None,
                "x": x,
                "y": y
            }


    # --------------------------- Không phải hàm chính ---------------------------
    
    def _get_ship_component(self, target_name, x, y):
        placement = db.session.scalar(
            db.select(ShipPlacement)
            .where(ShipPlacement.game_id == self.game.id)
            .where(ShipPlacement.owner == target_name)
        )
        if not placement:
            print(f"[DEBUG] không tìm thấy bảng placement của {target_name}")
            return None
        if not placement.ship_data:
            print(f"[DEBUG] không tìm thấy bảng ship_data của {target_name}")
            return None
        
        data = json.loads(placement.ship_data)
        for ship_name, info in data.items():
            coords = info.get('positions', {})
            if [x, y] in coords:
                return ship_name, coords
        return None

    def _is_component_sunk(self, component, board):
        """True nếu không có component chưa bị bắn"""
        for (x,y) in component:
            if board[x][y] == 1:
                return False
        return True

    def _is_ship_sunk(self, owner, ship_name, board):
        """Kiểm tra nếu toàn bộ tàu đã bị trúng"""
        for (x, y) in self.ship_positions[owner][ship_name]:
            if board[x][y] not in (2, 4):
                return False
        return True

    def _mark_component_sunk(self, component, board):
        print(f"[DEBUG] Đánh dấu component đã chìm: {component}")
        for (x,y) in component:
            board[x][y] = 4


    def _all_ships_sunk(self, board):
        """Kiểm tra nếu toàn bộ tàu đã bị bắn chìm"""
        for row in board:
            for cell in row:
                if cell == 1:  # vẫn còn phần tàu chưa bị bắn
                    return False
        return True
    
    def _record_ship_sunk(self, owner_name, ship_name):
        placement = db.session.scalar(
            db.select(ShipPlacement)
            .where(ShipPlacement.game_id == self.game.id)
            .where(ShipPlacement.owner == owner_name)
        )
        if not placement or not placement.ship_data:
            return

        data = json.loads(placement.ship_data)
        if ship_name in data:
            data[ship_name]["sunked"] = True
            placement.ship_data = json.dumps(data)
            db.session.commit()

        print(f"[DEBUG] Đánh dấu {ship_name} của {owner_name} là đã chìm")
