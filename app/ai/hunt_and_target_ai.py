import random
from app import db
from app.ai.ai_interface import BaseAI
from app.models import AIState

# 0: ô trống
# 1: ô có tàu
# 2: bắn trúng
# 3: bắng trượt 
# 4: chìm

class HuntAndTargetAI(BaseAI):
    """
    Heuristic Hill-Climbing Hunt & Target AI
    """

    dx = [-1, 1, 0, 0]
    dy = [0, 0, -1, 1]
    # ================ INIT & STATE MANAGEMENT =================
    def __init__(self, game, name="HuntAndTargetAI"):
        super().__init__(game, name)
        self.game_id = game.id
        self.ai_name = name
        self.state = self._load_state()
    
    def _load_state(self):
        state_record = AIState.query.filter_by(
            game_id = self.game_id,
            ai_name = self.ai_name
        ).first()

        if state_record:
            # nạp dữ liệu trạng thái của phát bắn cũ từ db
            self.current_hits = state_record.current_hits or []
            self.direction = state_record.direction
        else:
            # khởi tạo trạng thái mới nếu chưa có
            self.current_hits = [] # danh sách các vị trí đã bắn trúng
            self.direction = None 
        
       
    def _save_state(self):
        # Lưu trạng thái từ RAM xuống db
        state_record = AIState.query.filter_by(
            game_id = self.game_id,
            ai_name = self.ai_name
        ).first()
        
        if not state_record:
            state_record = AIState(
                game_id = self.game_id,
                ai_name = self.ai_name
            )
            db.session.add(state_record)
        
        state_record.current_hits = self.current_hits
        state_record.direction = self.direction

    # ================= PLACE SHIPS =================
    def place_ships(self):
        self.auto_place_ships(self.name)

    # ================= MAIN LOOP =================
    def make_shot(self, attacker_name, target_name):
        board = self.get_board(target_name)
        if not board:
            return {"result": "invalid", "x": -1, "y": -1}

        # Hill-climbing: chọn successor tốt nhất
        successors = self._generate_successors(board)
        if not successors:
            return {"result": "no_move", "x": -1, "y": -1}

        # Best successor theo heuristic
        best_score = max(move[2] for move in successors)
        best_moves = [move for move in successors if move[2] == best_score]
                         
        shoot = best_moves[0]
        # shoot = random.choice(best_moves)  
        x, y = shoot[0], shoot[1]
        
        result = self.shoot(attacker_name, target_name, x, y) # hit/miss/sunk dict
        self._update_state(result, x, y)
        
        # cập nhật thêm thông tin tọa độ vào result
        result["x"] = x
        result["y"] = y
        
        self._save_state()  # lưu trạng thái AI sau mỗi phát bắn
        return result

    # ================= SUCCESSOR GENERATION =================
    def _generate_successors(self, board):
        """
        Trả về danh sách successors có dạng (x, y, value)
        """
        successors = []

        # ===== TARGET MODE =====
        if self.current_hits:
            moves = []
            if self.direction:
                # TH1: đã suy luận được hướng → ưu tiên bắn theo hướng đó
                moves.extend(self._directional_moves(board, value=100))
            if not moves:
                self.direction = None
                # TH2: chưa suy luận được hướng → bắn xung quanh các hit hiện
                moves.extend(self._neighbor_moves(board, value=80))
                    
            if moves:
                return moves

         # ===== HUNT MODE (PARITY) =====
        for x in range(10):
            for y in range(10):
                if board[x][y] not in (2, 3, 4):
                    if (x + y) % 2 == 0:
                        value = 10 
                    else:
                        value = 1
                    successors.append((x, y, value))

        return successors

    # ================= HEURISTIC MOVES =================
    def _neighbor_moves(self, board, value):
        moves = []
        checked_moves = set()
        
        for (hx, hy) in self.current_hits:
            for i in range(4):
                x = hx + self.dx[i]
                y = hy + self.dy[i]
                if self._valid(board, x, y) and (x, y) not in checked_moves:
                    moves.append((x, y, value))
                    checked_moves.add((x, y))

        return moves

    def _directional_moves(self, board, value):
        moves = []
        hits = self.current_hits

        if self.direction == "V":
            y = hits[0][1] # cùng 1 cột
            xs = [x for x, _ in hits] # tập các tọa độ x
            candidates = [(min(xs) - 1, y), (max(xs) + 1, y)] # lấy 2 đầu
        else:
            x = hits[0][0] # cùng 1 hàng
            ys = [y for _, y in hits] # tập các tọa độ y 
            candidates = [(x, min(ys) - 1), (x, max(ys) + 1)] # lấy 2 đầu

        for x, y in candidates:
            if self._valid(board, x, y):
                moves.append((x, y, value))

        return moves

    # ================= STATE UPDATE =================
    def _update_state(self, result, x, y):
        if result["result"] == "hit":
            self.current_hits.append((x, y)) # thêm vị trí trúng vào danh sách
            if len(self.current_hits) >= 2:
               new_direction = self._detect_direction(x, y)
               if new_direction:
                   self.direction = new_direction

        elif result["result"] == "sunk":
            sunk_cells = result.get("comp", [])
            
            if not sunk_cells:
                self.current_hits.clear()
                self.direction = None
                return
            
            self.current_hits = [h for h in self.current_hits if h not in sunk_cells]
            self.direction = None

    def _detect_direction(self, current_x, current_y):
        # so sánh hit mới nhất với các hit cũ trong current_hits để xem có tạo thành 1 hướng hay không
        for (hx, hy) in reversed(self.current_hits[:-1]):
            if hx == current_x and abs(hy - current_y) == 1:
                return "H"
            if hy == current_y and abs(hx - current_x) == 1:
                return "V"
        return self.direction
     
    # ================= UTIL =================
    def _valid(self, board, x, y):
        return (
            0 <= x < 10 and
            0 <= y < 10 and 
            board[x][y] not in (2, 3, 4)
        )
