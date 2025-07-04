import tkinter as tk
from tkinter import messagebox, simpledialog
import threading, time, sys, copy
import lan_socket

SQUARE_SIZE = 64
UNICODE = {
    'white': {'K':'\u2654','Q':'\u2655','R':'\u2656','B':'\u2657','N':'\u2658','P':'\u2659'},
    'black': {'K':'\u265A','Q':'\u265B','R':'\u265C','B':'\u265D','N':'\u265E','P':'\u265F'}
}

class Piece:
    def __init__(self, kind, color):
        self.kind   = kind            # 'K','Q','R','B','N','P'
        self.color  = color           # 'white' / 'black'
        self.moved  = False           # for castling / initial-pawn

    def char(self):
        return UNICODE[self.color][self.kind]

class Board:
    def __init__(self):
        self.grid      = [[None]*8 for _ in range(8)]
        self.turn      = 'white'
        self.en_passant_target = None   # (r,c) square *behind* a just-double-pushed pawn
        self._setup()

    # ——— initial setup ———
    def _setup(self):
        for c in range(8):
            self.grid[6][c] = Piece('P', 'white')
            self.grid[1][c] = Piece('P', 'black')
        order = ['R','N','B','Q','K','B','N','R']
        for c, k in enumerate(order):
            self.grid[7][c] = Piece(k, 'white')
            self.grid[0][c] = Piece(k, 'black')

    # ——— helpers ———
    def inside(self, r, c):     return 0 <= r < 8 and 0 <= c < 8
    def get   (self, r, c):     return self.grid[r][c] if self.inside(r, c) else None
    def king_pos(self, color):
        for r in range(8):
            for c in range(8):
                p = self.get(r, c)
                if p and p.kind == 'K' and p.color == color:
                    return r, c

    # ——— move execution (assumes already legal) ———
    def move(self, sr, sc, tr, tc):
        piece = self.get(sr, sc)
        target = self.get(tr, tc)
        self.en_passant_target = None

        # en-passant capture
        if piece.kind == 'P' and (tr, tc) == self._en_passant_capture_sq(sr, sc):
            cap_row = tr + (1 if piece.color == 'white' else -1)
            self.grid[cap_row][tc] = None

        # castling: move rook too
        if piece.kind == 'K' and abs(tc - sc) == 2:
            if tc > sc:   # king-side
                rook_src, rook_dst = (sr, 7), (sr, 5)
            else:         # queen-side
                rook_src, rook_dst = (sr, 0), (sr, 3)
            self.grid[rook_dst[0]][rook_dst[1]] = self.get(*rook_src)
            self.grid[rook_src[0]][rook_src[1]] = None
            self.grid[rook_dst[0]][rook_dst[1]].moved = True

        # 2-square pawn push → set en-passant target
        if piece.kind == 'P' and abs(tr - sr) == 2:
            mid = (sr + tr)//2
            self.en_passant_target = (mid, tc)

        # promotion (queen auto)
        if piece.kind == 'P' and tr in (0, 7):
            piece.kind = 'Q'

        # move the piece
        self.grid[tr][tc] = piece
        self.grid[sr][sc] = None
        piece.moved = True
        self.turn = 'black' if self.turn == 'white' else 'white'

    # ——— attack / check helpers ———
    def _attacks_from(self, r, c):
        p = self.get(r, c)
        if not p: return []
        color = p.color
        opp   = 'black' if color == 'white' else 'white'
        moves = []

        if p.kind == 'P':
            dir_ = -1 if color == 'white' else 1
            for dc in (-1, 1):
                nr, nc = r + dir_, c + dc
                if self.inside(nr, nc):
                    moves.append((nr, nc))

        elif p.kind == 'N':
            for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                nr, nc = r + dr, c + dc
                if self.inside(nr, nc):
                    moves.append((nr, nc))

        elif p.kind in ('B', 'R', 'Q'):
            dirs = []
            if p.kind in ('B','Q'):
                dirs += [(1,1),(1,-1),(-1,1),(-1,-1)]
            if p.kind in ('R','Q'):
                dirs += [(1,0),(-1,0),(0,1),(0,-1)]
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                while self.inside(nr, nc):
                    moves.append((nr, nc))
                    if self.get(nr, nc): break
                    nr += dr; nc += dc

        elif p.kind == 'K':
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr == dc == 0: continue
                    nr, nc = r + dr, c + dc
                    if self.inside(nr, nc):
                        moves.append((nr, nc))
        return moves

    def is_attacked(self, r, c, by_color):
        for rr in range(8):
            for cc in range(8):
                q = self.get(rr, cc)
                if q and q.color == by_color:
                    if (r, c) in self._piece_legal_attacks(rr, cc):
                        return True
        return False

    # same as _attacks_from but ignores castling/en-p and considers board occupancy
    def _piece_legal_attacks(self, r, c):
        p = self.get(r, c)
        if not p: return []
        color = p.color
        res   = []

        if p.kind == 'P':
            dir_ = -1 if color == 'white' else 1
            for dc in (-1, 1):
                nr, nc = r + dir_, c + dc
                if self.inside(nr, nc):
                    res.append((nr, nc))
            # en-passant: the pawn *attacks* the en-passant target square
            if self.en_passant_target:
                etr, etc = self.en_passant_target
                if abs(etc - c) == 1 and etr == r + dir_:
                    res.append((etr, etc))

        elif p.kind == 'N':
            for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                nr, nc = r + dr, c + dc
                if self.inside(nr, nc):
                    res.append((nr, nc))

        elif p.kind in ('B','R','Q'):
            dirs = []
            if p.kind in ('B','Q'):
                dirs += [(1,1),(1,-1),(-1,1),(-1,-1)]
            if p.kind in ('R','Q'):
                dirs += [(1,0),(-1,0),(0,1),(0,-1)]
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                while self.inside(nr, nc):
                    res.append((nr, nc))
                    if self.get(nr, nc): break
                    nr += dr; nc += dc

        elif p.kind == 'K':
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr == dc == 0: continue
                    nr, nc = r + dr, c + dc
                    if self.inside(nr, nc):
                        res.append((nr, nc))
        return res

    def in_check(self, color):
        kr, kc = self.king_pos(color)
        opp = 'black' if color == 'white' else 'white'
        return self.is_attacked(kr, kc, opp)

    # ——— move-generation ———
    def legal_moves(self, r, c):
        p = self.get(r, c)
        if not p or p.color != self.turn: return []

        moves = []
        color = p.color
        opp   = 'black' if color == 'white' else 'white'
        dir_  = -1 if color == 'white' else 1

        if p.kind == 'P':
            nr = r + dir_
            # single forward
            if self.inside(nr, c) and not self.get(nr, c):
                moves.append((nr, c))
                # double forward
                start = 6 if color == 'white' else 1
                if r == start and not self.get(nr + dir_, c):
                    moves.append((nr + dir_, c))
            # captures
            for dc in (-1, 1):
                nc = c + dc
                if self.inside(nr, nc):
                    tgt = self.get(nr, nc)
                    if tgt and tgt.color == opp:
                        moves.append((nr, nc))
            # en-passant
            if self.en_passant_target:
                etr, etc = self.en_passant_target
                if etr == nr and abs(etc - c) == 1:
                    moves.append((etr, etc))

        elif p.kind == 'N':
            for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                nr, nc = r + dr, c + dc
                if self.inside(nr, nc):
                    tgt = self.get(nr, nc)
                    if not tgt or tgt.color == opp:
                        moves.append((nr, nc))

        elif p.kind in ('B','R','Q'):
            dirs = []
            if p.kind in ('B','Q'):
                dirs += [(1,1),(1,-1),(-1,1),(-1,-1)]
            if p.kind in ('R','Q'):
                dirs += [(1,0),(-1,0),(0,1),(0,-1)]
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                while self.inside(nr, nc):
                    tgt = self.get(nr, nc)
                    if not tgt:
                        moves.append((nr, nc))
                    else:
                        if tgt.color == opp:
                            moves.append((nr, nc))
                        break
                    nr += dr; nc += dc

        elif p.kind == 'K':
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr == dc == 0: continue
                    nr, nc = r + dr, c + dc
                    if self.inside(nr, nc):
                        tgt = self.get(nr, nc)
                        if not tgt or tgt.color == opp:
                            moves.append((nr, nc))
            # castling
            if not p.moved and not self.in_check(color):
                # king-side
                if self._castle_clear(r, c, (r, 7), (r, 5), (r,6)):
                    moves.append((r, c+2))
                # queen-side
                if self._castle_clear(r, c, (r, 0), (r, 3), (r,2,1)):
                    moves.append((r, c-2))

        # —— filter out moves that leave own king in check ——
        legal = []
        for (tr, tc) in moves:
            board_copy = copy.deepcopy(self)
            board_copy.move(r, c, tr, tc)
            if not board_copy.in_check(color):
                legal.append((tr, tc))
        return legal

    # helper: castling path clear & rook unmoved & squares not attacked
    def _castle_clear(self, kr, kc, rook_sq, between_sq, king_travel):
        rr, rc = rook_sq
        rook = self.get(rr, rc)
        if not rook or rook.kind != 'R' or rook.moved or rook.color != self.turn:
            return False
        # squares between king and rook must be empty
        bqs = [between_sq] if isinstance(between_sq[0], int) else between_sq
        for sq in bqs:
            if self.get(*sq): return False
        # king path squares must not be attacked
        opp = 'black' if self.turn == 'white' else 'white'
        path = [ (kr, kc+i) for i in (1,2) ] if king_travel==(kr, kc+2) else [ (kr, kc-1), (kr, kc-2) ]
        for sq in path:
            if self.is_attacked(*sq, by_color=opp): return False
        return True

    # en-passant capture square helper
    def _en_passant_capture_sq(self, sr, sc):
        p = self.get(sr, sc)
        if p.kind != 'P' or not self.en_passant_target: return None
        etr, etc = self.en_passant_target
        dir_ = -1 if p.color == 'white' else 1
        if etr == sr + dir_ and abs(etc - sc) == 1:
            return (etr, etc)

    # ——— whole–position helpers ———
    def any_legal_move(self, color):
        for r in range(8):
            for c in range(8):
                q = self.get(r, c)
                if q and q.color == color and self.legal_moves(r, c):
                    return True
        return False

    def game_state(self):
        """Return ('normal' | 'check' | 'mate' | 'stalemate', for side *to move*)"""
        if self.any_legal_move(self.turn):
            return 'check' if self.in_check(self.turn) else 'normal'
        else:
            return 'mate' if self.in_check(self.turn) else 'stalemate'

# ——————————————————————————————————  GUI  ———————————————————————————————————

class ChessGUI:
    def __init__(self):
        self.board = Board()

        self.root   = tk.Tk()
        self.root.title("LAN Chess")
        self.canvas = tk.Canvas(self.root, width=8*SQUARE_SIZE, height=8*SQUARE_SIZE)
        self.canvas.pack()
        self.status = tk.Label(self.root, font=('Arial', 12))
        self.status.pack()

        # Networking setup
        choice = simpledialog.askstring("Network", "Type 'host' to host, or enter host-IP to join:")
        if not choice: sys.exit(0)
        if choice.lower() == 'host':
            self.is_host  = True
            self.color    = 'white'
            self.opponent = 'black'
        else:
            self.is_host  = False
            self.host_ip  = choice.strip()
            self.color    = 'black'
            self.opponent = 'white'

        self.selected  = None
        self.highlight = []
        self.sending   = False

        self.canvas.bind('<Button-1>', self.on_click)
        self.draw()
        self.update_status()

        threading.Thread(target=self.net_loop, daemon=True).start()

    # ——— drawing ———
    def rc(self, x, y):  return y//SQUARE_SIZE, x//SQUARE_SIZE
    def center(self, r, c): return c*SQUARE_SIZE+SQUARE_SIZE//2, r*SQUARE_SIZE+SQUARE_SIZE//2

    def draw(self):
        self.canvas.delete('all')
        light, dark = '#EEEED2', '#769656'
        for r in range(8):
            for c in range(8):
                self.canvas.create_rectangle(
                    c*SQUARE_SIZE, r*SQUARE_SIZE,
                    (c+1)*SQUARE_SIZE, (r+1)*SQUARE_SIZE,
                    fill= light if (r+c)%2==0 else dark, outline='')
        for r, c in self.highlight:
            self.canvas.create_rectangle(
                    c*SQUARE_SIZE, r*SQUARE_SIZE,
                    (c+1)*SQUARE_SIZE, (r+1)*SQUARE_SIZE,
                    fill='yellow', stipple='gray25', outline='')
        for r in range(8):
            for c in range(8):
                p = self.board.get(r, c)
                if p:
                    x, y = self.center(r, c)
                    self.canvas.create_text(x, y, text=p.char(), font=('Arial', 36))

    def update_status(self):
        st = f"You are {self.color}   |   Turn: {self.board.turn}"
        gs = self.board.game_state()
        if gs == 'check' and self.board.turn == self.color:
            st += "   —  YOU are in check!"
        elif gs == 'check':
            st += "   —  Opponent in check."
        self.status.config(text=st)

    # ——— move encoding helpers ———
    def encode(self, sr, sc, tr, tc):
        files = "abcdefgh"
        return f"{files[sc]}{8-sr}{files[tc]}{8-tr}"

    def decode(self, s):
        files = "abcdefgh"
        sc = files.index(s[0]); sr = 8 - int(s[1])
        tc = files.index(s[2]); tr = 8 - int(s[3])
        return sr, sc, tr, tc

    # ——— mouse interaction ———
    def on_click(self, event):
        if self.board.turn != self.color:
            return

        r, c = self.rc(event.x, event.y)
        if self.selected:
            if (r, c) in self.highlight:
                sr, sc = self.selected
                move = self.encode(sr, sc, r, c)
                self.board.move(sr, sc, r, c)
                self.selected  = None
                self.highlight = []
                self.draw()
                self.post_move_updates()

                self.sending = True
                threading.Thread(target=self.send_move, args=(move,), daemon=True).start()
            else:
                self.selected  = None
                self.highlight = []
        else:
            p = self.board.get(r, c)
            if p and p.color == self.color:
                self.selected  = (r, c)
                self.highlight = self.board.legal_moves(r, c)
        self.draw()

    # ——— network helpers ———
    def send_move(self, mv):
        try:
            if self.is_host:
                lan_socket.server_mode(mv.encode(), 'white')
            else:
                lan_socket.client_mode(mv.encode(), 'white', self.host_ip)
        finally:
            self.sending = False

        # ——— receive ONE move from the other side ———
    def recv_move(self):
        try:
            if self.is_host:                       # host listens
                return lan_socket.server_mode(b'', 'black')
            else:                                  # guest connects
                return lan_socket.client_mode(b'', 'black', self.host_ip)
        except (ConnectionResetError, ConnectionRefusedError, OSError):
            # remote isn’t ready yet → just try again on the next pass
            return ''

    # apply a move received from the other side, on UI thread
    def _apply_remote_move(self, mv):
        sr, sc, tr, tc = self.decode(mv)
        self.board.move(sr, sc, tr, tc)
        self.draw()
        self.post_move_updates()

    def net_loop(self):
        while True:
            if not self.sending and self.board.turn == self.opponent:
                mv = self.recv_move()
                if mv:
                    self.root.after(0, self._apply_remote_move, mv)
            time.sleep(0.1)

    # ——— post-move game-state checks ———
    def post_move_updates(self):
        gs = self.board.game_state()
        if gs == 'mate':
            winner = 'white' if self.board.turn == 'black' else 'black'
            messagebox.showinfo("Check-mate", f"{winner.capitalize()} wins by check-mate!")
        elif gs == 'stalemate':
            messagebox.showinfo("Stalemate", "Draw by stalemate.")
        elif gs == 'check':
            messagebox.showinfo("Check", "Check!")
        self.update_status()

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    ChessGUI().run()
