import tkinter as tk
from tkinter import messagebox, simpledialog
import threading, time, sys
import lan_socket

SQUARE_SIZE = 64
UNICODE = {
    'white': {'K':'\u2654','Q':'\u2655','R':'\u2656','B':'\u2657','N':'\u2658','P':'\u2659'},
    'black': {'K':'\u265A','Q':'\u265B','R':'\u265C','B':'\u265D','N':'\u265E','P':'\u265F'}
}

class Piece:
    def __init__(self, kind, color):
        self.kind = kind          # 'K','Q','R','B','N','P'
        self.color = color
    def char(self):
        return UNICODE[self.color][self.kind]

class Board:
    def __init__(self):
        self.grid = [[None]*8 for _ in range(8)]
        self.turn = 'white'
        self._setup()

    def _setup(self):
        # Pawns
        for c in range(8):
            self.grid[6][c] = Piece('P', 'white')
            self.grid[1][c] = Piece('P', 'black')
        # Back rank
        order = ['R','N','B','Q','K','B','N','R']
        for c, k in enumerate(order):
            self.grid[7][c] = Piece(k, 'white')
            self.grid[0][c] = Piece(k, 'black')

    # ——— helpers ———
    def inside(self, r, c):     return 0 <= r < 8 and 0 <= c < 8
    def get   (self, r, c):     return self.grid[r][c] if self.inside(r, c) else None

    # ——— moves ———
    def move(self, sr, sc, tr, tc):
        self.grid[tr][tc] = self.grid[sr][sc]
        self.grid[sr][sc] = None
        self.turn = 'black' if self.turn == 'white' else 'white'

    def legal_moves(self, r, c):
        p = self.get(r, c)
        if not p or p.color != self.turn:
            return []

        moves = []
        if p.kind == 'P':
            dir_   = -1 if p.color == 'white' else  1
            start  =  6 if p.color == 'white' else 1
            nr = r + dir_
            # forward
            if self.inside(nr, c) and self.get(nr, c) is None:
                moves.append((nr, c))
                # double push
                if r == start and self.get(nr + dir_, c) is None:
                    moves.append((nr + dir_, c))
            # captures
            for dc in (-1, 1):
                nc = c + dc
                if self.inside(nr, nc):
                    t = self.get(nr, nc)
                    if t and t.color != p.color:
                        moves.append((nr, nc))

        elif p.kind == 'N':
            for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                nr, nc = r + dr, c + dc
                if self.inside(nr, nc):
                    t = self.get(nr, nc)
                    if t is None or t.color != p.color:
                        moves.append((nr, nc))

        elif p.kind in ('B', 'R', 'Q'):
            dirs = []
            if p.kind in ('B', 'Q'):
                dirs += [(1,1),(1,-1),(-1,1),(-1,-1)]
            if p.kind in ('R', 'Q'):
                dirs += [(1,0),(-1,0),(0,1),(0,-1)]
            moves += self._slide_moves(r, c, dirs, p.color)

        elif p.kind == 'K':
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr == dc == 0: continue
                    nr, nc = r + dr, c + dc
                    if self.inside(nr, nc):
                        t = self.get(nr, nc)
                        if t is None or t.color != p.color:
                            moves.append((nr, nc))
        return moves

    def _slide_moves(self, r, c, dirs, color):
        res = []
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            while self.inside(nr, nc):
                t = self.get(nr, nc)
                if t is None:
                    res.append((nr, nc))
                else:
                    if t.color != color:
                        res.append((nr, nc))
                    break
                nr += dr; nc += dc
        return res

# ——————————————————————————————————  GUI  ———————————————————————————————————

class ChessGUI:
    def __init__(self):
        self.board = Board()

        self.root   = tk.Tk()
        self.root.title("LAN Chess")
        self.canvas = tk.Canvas(self.root, width=8*SQUARE_SIZE, height=8*SQUARE_SIZE)
        self.canvas.pack()
        self.status = tk.Label(self.root)
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

        self.selected = None
        self.highlight = []
        self.sending  = False 

        self.canvas.bind('<Button-1>', self.on_click)
        self.draw()
        self.update_status()

        # background thread for incoming moves
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
        self.status.config(text=f"You are {self.color}.    Turn: {self.board.turn}")

    # ——— move encoding helpers ———
    def encode(self, sr, sc, tr, tc):
        files = "abcdefgh"
        return f"{files[sc]}{8-sr}{files[tc]}{8-tr}"

    def decode(self, s):
        files = "abcdefgh"
        sc = files.index(s[0]); sr = 8 - int(s[1])
        tc = files.index(s[2]); tr = 8 - int(s[3])
        return sr, sc, tr, tc

    # ──────────────────────────────────────────────────────────────
    # Mouse handler – left-click on the board
    # ──────────────────────────────────────────────────────────────
    def on_click(self, event):
        # Only act on our own turn
        if self.board.turn != self.color:
            return

        r, c = self.rc(event.x, event.y)      # board coordinates

        # ── CASE 1: we already have a piece selected ──────────────
        if self.selected:
            if (r, c) in self.highlight:      # clicked a highlighted square → make the move
                sr, sc = self.selected
                move = self.encode(sr, sc, r, c)

                # update local board
                self.board.move(sr, sc, r, c)
                self.selected  = None
                self.highlight = []
                self.draw()
                self.update_status()

                # tell the background thread we’re about to send
                self.sending = True
                threading.Thread(
                    target=self.send_move,
                    args=(move,),
                    daemon=True
                ).start()
            else:
                # clicked somewhere else → cancel selection
                self.selected  = None
                self.highlight = []

        # ── CASE 2: nothing selected yet ──────────────────────────
        else:
            p = self.board.get(r, c)
            if p and p.color == self.color:
                # select this piece and highlight legal moves
                self.selected  = (r, c)
                self.highlight = self.board.legal_moves(r, c)

        # always redraw after a click
        self.draw()

    # ——— networking helpers ———
    def send_move(self, mv):
        try:
            if self.is_host:
                lan_socket.server_mode(mv.encode(), 'white')
            else:
                lan_socket.client_mode(mv.encode(), 'white', self.host_ip)
        finally:
            self.sending = False     # ready to receive again

    def recv_move(self):
        if self.is_host:
            return lan_socket.server_mode(b'', 'black')
        else:
            return lan_socket.client_mode(b'', 'black', self.host_ip)

    # UI-thread wrapper for remote moves
    def _apply_remote_move(self, mv):
        sr, sc, tr, tc = self.decode(mv)
        self.board.move(sr, sc, tr, tc)
        self.draw()
        self.update_status()

    def net_loop(self):
        while True:
            if not self.sending and self.board.turn == self.opponent:
                mv = self.recv_move()
                if mv:
                    self.root.after(0, self._apply_remote_move, mv)
            time.sleep(0.1)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    ChessGUI().run()

