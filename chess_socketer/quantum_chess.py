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
        self.kind   = kind
        self.color  = color
        self.moved  = False
    def char(self):
        return UNICODE[self.color][self.kind]

class Board:
    def __init__(self):
        self.grid      = [[None]*8 for _ in range(8)]
        self.turn      = 'white'
        self.en_passant_target = None
        self._setup()

    def _setup(self):
        for c in range(8):
            self.grid[6][c] = Piece('P', 'white')
            self.grid[1][c] = Piece('P', 'black')
        order = ['R','N','B','Q','K','B','N','R']
        for c, k in enumerate(order):
            self.grid[7][c] = Piece(k, 'white')
            self.grid[0][c] = Piece(k, 'black')

    def inside(self, r, c):     return 0 <= r < 8 and 0 <= c < 8
    def get(self, r, c):        return self.grid[r][c] if self.inside(r, c) else None
    def king_pos(self, color):
        for r in range(8):
            for c in range(8):
                p = self.get(r, c)
                if p and p.kind == 'K' and p.color == color:
                    return r, c

    def move(self, sr, sc, tr, tc):
        piece = self.get(sr, sc)
        self.en_passant_target = None

        # en-passant capture
        if piece.kind == 'P' and (tr, tc) == self._en_passant_capture_sq(sr, sc):
            cap_row = tr + (1 if piece.color == 'white' else -1)
            self.grid[cap_row][tc] = None

        # castling
        if piece.kind == 'K' and abs(tc - sc) == 2:
            if tc > sc:
                rook_src, rook_dst = (sr, 7), (sr, 5)
            else:
                rook_src, rook_dst = (sr, 0), (sr, 3)
            self.grid[rook_dst[0]][rook_dst[1]] = self.get(*rook_src)
            self.grid[rook_src[0]][rook_src[1]] = None
            self.grid[rook_dst[0]][rook_dst[1]].moved = True

        # double pawn push
        if piece.kind == 'P' and abs(tr - sr) == 2:
            mid = (sr + tr)//2
            self.en_passant_target = (mid, tc)

        # promotion
        if piece.kind == 'P' and tr in (0, 7):
            piece.kind = 'Q'

        # regular move
        self.grid[tr][tc] = piece
        self.grid[sr][sc] = None
        piece.moved = True
        self.turn = 'black' if self.turn == 'white' else 'white'

    def _attacks_from(self, r, c):
        p = self.get(r, c)
        if not p: return []
        color = p.color
        res = []
        if p.kind == 'P':
            d = -1 if color=='white' else 1
            for dc in (-1,1):
                nr, nc = r+d, c+dc
                if self.inside(nr, nc):
                    res.append((nr, nc))
        elif p.kind == 'N':
            for dr,dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                nr, nc = r+dr, c+dc
                if self.inside(nr, nc):
                    res.append((nr, nc))
        elif p.kind in ('B','R','Q'):
            dirs = []
            if p.kind in ('B','Q'): dirs += [(1,1),(1,-1),(-1,1),(-1,-1)]
            if p.kind in ('R','Q'): dirs += [(1,0),(-1,0),(0,1),(0,-1)]
            for dr,dc in dirs:
                nr, nc = r+dr, c+dc
                while self.inside(nr, nc):
                    res.append((nr, nc))
                    if self.get(nr, nc): break
                    nr += dr; nc += dc
        elif p.kind=='K':
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr==dc==0: continue
                    nr, nc = r+dr, c+dc
                    if self.inside(nr, nc):
                        res.append((nr, nc))
        return res

    def is_attacked(self, r, c, by_color):
        for rr in range(8):
            for cc in range(8):
                q = self.get(rr, cc)
                if q and q.color==by_color:
                    if (r,c) in self._piece_legal_attacks(rr,cc):
                        return True
        return False

    def _piece_legal_attacks(self, r, c):
        # like _attacks_from but counts occupancy & en-passant
        p = self.get(r, c)
        if not p: return []
        color = p.color; opp = 'black' if color=='white' else 'white'
        res = []
        if p.kind == 'P':
            d = -1 if color=='white' else 1
            for dc in (-1,1):
                nr, nc = r+d, c+dc
                if self.inside(nr, nc):
                    res.append((nr, nc))
            if self.en_passant_target:
                etr,etc = self.en_passant_target
                if etr==r+d and abs(etc-c)==1:
                    res.append((etr,etc))
        elif p.kind=='N':
            for dr,dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                nr, nc = r+dr, c+dc
                if self.inside(nr,nc):
                    res.append((nr,nc))
        elif p.kind in ('B','R','Q'):
            dirs=[]
            if p.kind in ('B','Q'): dirs+=[(1,1),(1,-1),(-1,1),(-1,-1)]
            if p.kind in ('R','Q'): dirs+=[(1,0),(-1,0),(0,1),(0,-1)]
            for dr,dc in dirs:
                nr,nc = r+dr,c+dc
                while self.inside(nr,nc):
                    res.append((nr,nc))
                    if self.get(nr,nc): break
                    nr+=dr; nc+=dc
        elif p.kind=='K':
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr==dc==0: continue
                    nr,nc = r+dr,c+dc
                    if self.inside(nr,nc):
                        res.append((nr,nc))
        return res

    def in_check(self, color):
        kr,kc = self.king_pos(color)
        return self.is_attacked(kr, kc, 'black' if color=='white' else 'white')

    def legal_moves(self, r, c):
        p = self.get(r, c)
        if not p or p.color!=self.turn: return []
        moves = []
        color, opp = p.color, ('black' if p.color=='white' else 'white')
        if p.kind=='P':
            d = -1 if color=='white' else 1
            nr = r+d
            # forward
            if self.inside(nr,c) and not self.get(nr,c):
                moves.append((nr,c))
                start = 6 if color=='white' else 1
                if r==start and not self.get(nr+d, c):
                    moves.append((nr+d, c))
            # captures
            for dc in (-1,1):
                nc=c+dc
                if self.inside(nr,nc):
                    tgt = self.get(nr,nc)
                    if tgt and tgt.color==opp:
                        moves.append((nr,nc))
            # en-passant
            if self.en_passant_target:
                etr,etc = self.en_passant_target
                if etr==nr and abs(etc-c)==1:
                    moves.append((etr,etc))

        elif p.kind=='N':
            for dr,dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                nr,nc=r+dr,c+dc
                if self.inside(nr,nc):
                    tgt=self.get(nr,nc)
                    if not tgt or tgt.color==opp:
                        moves.append((nr,nc))

        elif p.kind in ('B','R','Q'):
            dirs=[]
            if p.kind in ('B','Q'): dirs+=[(1,1),(1,-1),(-1,1),(-1,-1)]
            if p.kind in ('R','Q'): dirs+=[(1,0),(-1,0),(0,1),(0,-1)]
            for dr,dc in dirs:
                nr,nc=r+dr,c+dc
                while self.inside(nr,nc):
                    tgt=self.get(nr,nc)
                    if not tgt:
                        moves.append((nr,nc))
                    else:
                        if tgt.color==opp:
                            moves.append((nr,nc))
                        break
                    nr+=dr; nc+=dc

        elif p.kind=='K':
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr==dc==0: continue
                    nr,nc=r+dr,c+dc
                    if self.inside(nr,nc):
                        tgt=self.get(nr,nc)
                        if not tgt or tgt.color==opp:
                            moves.append((nr,nc))
            # castling
            if not p.moved and not self.in_check(color):
                # king-side
                if self._castle_clear(r, c, (r,7), [(r,5),(r,6)], [(r,5),(r,6)]):
                    moves.append((r, c+2))
                # queen-side
                if self._castle_clear(r, c, (r,0), [(r,1),(r,2),(r,3)], [(r,3),(r,2)]):
                    moves.append((r, c-2))

        # filter out moves leaving king in check
        legal=[]
        for tr,tc in moves:
            copyb = copy.deepcopy(self)
            copyb.move(r,c,tr,tc)
            if not copyb.in_check(color):
                legal.append((tr,tc))
        return legal

    def _castle_clear(self, kr, kc, rook_sq, between_sqs, path_sqs):
        rr,rc=rook_sq
        rook=self.get(rr,rc)
        if not rook or rook.kind!='R' or rook.moved or rook.color!=self.turn:
            return False
        for (r,c) in between_sqs:
            if self.get(r,c): return False
        opp='black' if self.turn=='white' else 'white'
        for (r,c) in path_sqs:
            if self.is_attacked(r,c,opp): return False
        return True

    def _en_passant_capture_sq(self, sr, sc):
        p=self.get(sr,sc)
        if p.kind!='P' or not self.en_passant_target: return None
        etr,etc = self.en_passant_target
        d = -1 if p.color=='white' else 1
        if etr==sr+d and abs(etc-sc)==1:
            return (etr,etc)

    def any_legal_move(self, color):
        for r in range(8):
            for c in range(8):
                q=self.get(r,c)
                if q and q.color==color and self.legal_moves(r,c):
                    return True
        return False

    def game_state(self):
        if self.any_legal_move(self.turn):
            return 'check' if self.in_check(self.turn) else 'normal'
        else:
            return 'mate' if self.in_check(self.turn) else 'stalemate'

class ChessGUI:
    def __init__(self):
        self.board = Board()

        # ── Tk setup ───────────────────────────────────────────────
        self.root   = tk.Tk()
        self.root.title("LAN Chess")
        self.canvas = tk.Canvas(self.root, width=8*SQUARE_SIZE, height=8*SQUARE_SIZE)
        self.canvas.pack()
        self.status = tk.Label(self.root, font=('Arial', 12))
        self.status.pack()

        # ── Networking side choice ────────────────────────────────
        choice = simpledialog.askstring("Network",
                                        "Type 'host' to host, or enter host-IP to join:")
        if not choice:
            sys.exit(0)
        if choice.lower() == 'host':
            self.is_host, self.color, self.opponent = True,  'white', 'black'
        else:
            self.is_host, self.host_ip = False, choice.strip()
            self.color,   self.opponent = 'black', 'white'

        # flip → show Black’s perspective
        self.flip = (self.color == 'black')

        # ── GUI/session state ─────────────────────────────────────
        self.selected  = None      # (row, col) of currently selected piece
        self.highlight = []        # list of legal-move squares to tint
        self.sending   = False     # True while a send-thread owns the port

        # ── Bindings & start ──────────────────────────────────────
        self.canvas.bind('<Button-1>', self.on_click)
        self.draw()
        self.update_status()

        # background thread for incoming moves
        threading.Thread(target=self.net_loop, daemon=True).start()

    # ──────────────────────────────────────────────────────────────
    # Helpers: coordinate transforms
    # ──────────────────────────────────────────────────────────────
    def board_to_screen(self, br, bc):
        """(board-row,col) → canvas pixel centre (x,y)"""
        sr  = 7 - br if self.flip else br
        sc  = 7 - bc if self.flip else bc
        x   = sc * SQUARE_SIZE + SQUARE_SIZE // 2
        y   = sr * SQUARE_SIZE + SQUARE_SIZE // 2
        return x, y

    def rc(self, x, y):
        """Canvas click → (board-row, board-col)"""
        sr = y // SQUARE_SIZE
        sc = x // SQUARE_SIZE
        return (7 - sr, 7 - sc) if self.flip else (sr, sc)

    # ──────────────────────────────────────────────────────────────
    # Drawing
    # ──────────────────────────────────────────────────────────────
    def draw(self):
        self.canvas.delete('all')
        light, dark = '#EEEED2', '#769656'

        # squares
        for br in range(8):
            for bc in range(8):
                sr = 7 - br if self.flip else br
                sc = 7 - bc if self.flip else bc
                color = light if (br + bc) % 2 == 0 else dark
                self.canvas.create_rectangle(
                    sc * SQUARE_SIZE, sr * SQUARE_SIZE,
                    (sc + 1) * SQUARE_SIZE, (sr + 1) * SQUARE_SIZE,
                    fill=color, outline=''
                )

        # highlights
        for br, bc in self.highlight:
            sr = 7 - br if self.flip else br
            sc = 7 - bc if self.flip else bc
            self.canvas.create_rectangle(
                sc * SQUARE_SIZE, sr * SQUARE_SIZE,
                (sc + 1) * SQUARE_SIZE, (sr + 1) * SQUARE_SIZE,
                fill='yellow', stipple='gray25', outline=''
            )

        # pieces
        for br in range(8):
            for bc in range(8):
                p = self.board.get(br, bc)
                if p:
                    x, y = self.board_to_screen(br, bc)
                    self.canvas.create_text(x, y, text=p.char(), font=('Arial', 36))

    def update_status(self):
        st = f"You are {self.color}   |   Turn: {self.board.turn}"
        gs = self.board.game_state()
        if gs == 'check' and self.board.turn == self.color:
            st += "   —  YOU are in check!"
        elif gs == 'check':
            st += "   —  Opponent in check."
        self.status.config(text=st)

    # ──────────────────────────────────────────────────────────────
    # Algebraic helpers for LAN
    # ──────────────────────────────────────────────────────────────
    def encode(self, sr, sc, tr, tc):
        files = "abcdefgh"
        return f"{files[sc]}{8-sr}{files[tc]}{8-tr}"

    def decode(self, s):
        files = "abcdefgh"
        sc = files.index(s[0]); sr = 8 - int(s[1])
        tc = files.index(s[2]); tr = 8 - int(s[3])
        return sr, sc, tr, tc

    # ──────────────────────────────────────────────────────────────
    # Mouse interaction
    # ──────────────────────────────────────────────────────────────
    def on_click(self, event):
        if self.board.turn != self.color:
            return

        r, c = self.rc(event.x, event.y)
        if self.selected:
            if (r, c) in self.highlight:
                sr, sc = self.selected
                move = self.encode(sr, sc, r, c)
                self.board.move(sr, sc, r, c)
                self.selected = None
                self.highlight = []
                self.draw()
                self.post_move_updates()

                self.sending = True
                threading.Thread(target=self.send_move, args=(move,), daemon=True).start()
            else:
                self.selected = None
                self.highlight = []
        else:
            p = self.board.get(r, c)
            if p and p.color == self.color:
                self.selected = (r, c)
                self.highlight = self.board.legal_moves(r, c)
        self.draw()

    # ──────────────────────────────────────────────────────────────
    # Networking wrappers
    # ──────────────────────────────────────────────────────────────
    def send_move(self, mv):
        try:
            if self.is_host:
                lan_socket.server_mode(mv.encode(), 'white')
            else:
                lan_socket.client_mode(mv.encode(), 'white', self.host_ip)
        finally:
            self.sending = False

    def recv_move(self):
        try:
            if self.is_host:
                return lan_socket.server_mode(b'', 'black')
            else:
                return lan_socket.client_mode(b'', 'black', self.host_ip)
        except (ConnectionResetError, ConnectionRefusedError, OSError):
            return ''

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

    # ──────────────────────────────────────────────────────────────
    # Post-move state / pop-ups
    # ──────────────────────────────────────────────────────────────
    def post_move_updates(self):
        gs = self.board.game_state()
        if gs == 'mate':
            winner = 'white' if self.board.turn == 'black' else 'black'
            messagebox.showinfo("Check-mate", f"{winner.capitalize()} wins!")
        elif gs == 'stalemate':
            messagebox.showinfo("Stalemate", "Draw by stalemate.")
        elif gs == 'check':
            messagebox.showinfo("Check", "Check!")
        self.update_status()

    # ──────────────────────────────────────────────────────────────
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    ChessGUI().run()
