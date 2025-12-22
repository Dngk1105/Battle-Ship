from app import db
from app.ai.ai_interface import BaseAI

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

    def __init__(self, name):
        super().__init__(name)
        self.current_hits = []   # state : lưu các ô đã bắn trúng nhưng chưa chìm tàu 
        self.direction = None    # "H" | "V"

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
        best_score = -1e9
        best_move = None
        for move  in successors:
            if move[2] > best_score:
                best_score = move[2]
                best_move = move
                
        x, y = best_move[0], best_move[1]
        
        result = self.shoot(attacker_name, target_name, x, y) # hit/miss/sunk dict
        self._update_state(result, x, y)
        
        result["x"] = x, result["y"] = y

        db.session.commit() # lưu kết quả bắn vào db
        return result

    # ================= SUCCESSOR GENERATION =================
    def _generate_successors(self, board):
        """
        Trả về danh sách successors có dạng (x, y, value)
        """
        successors = []

        # ===== TARGET MODE =====
        if self.current_hits:
            if self.direction:
                # TH1: đã suy luận được hướng → ưu tiên bắn theo hướng đó
                moves = self._directional_moves(board, value=100)
                for move in moves:
                    successors.append(move)
            else:
                # TH2: chưa suy luận được hướng → bắn các ô lân cận
                moves = self._neighbor_moves(board, value=80)
                for move in moves:
                    successors.append(move)
                    
            if successors:
                return successors

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
        x, y = self.current_hits[0] # chỉ cần lấy hit đầu tiên 
   
        for i in range(4):
            nx, ny = x + self.dx[i], y + self.dy[i]
            if self._valid(board, nx, ny):
                moves.append((nx, ny, value))

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
            self.current_hits.append((x, y))
            if len(self.current_hits) >= 2:
                # lấy ra 2 hit trúng đầu tiên
                x1, y1 = self.current_hits[0]
                x2 , y2 = self.current_hits[1]
                
                if x1 == x2:
                    self.direction = "H"
                elif y1 == y2:
                    self.direction = "V"

        elif result["result"] == "sunk":
            # local maximum reached → restart
            self.current_hits.clear()
            self.direction = None

    # ================= UTIL =================
    def _valid(self, board, x, y):
        return (
            0 <= x < 10 and
            0 <= y < 10 and 
            board[x][y] not in (2, 3, 4)
        )
