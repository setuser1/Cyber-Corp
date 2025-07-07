import tkinter as tk
from tkinter import messagebox, simpledialog
import threading, time, sys, random, copy
import lan_socket

SQUARE_SIZE = 64
UNICODE = {
    "white": {"K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙"},
    "black": {"K": "♚", "Q": "♛", "R": "♜", "B": "♝", "N": "♞", "P": "♟"},
}
FILES = "abcdefgh"


# ─────────────────────────────────────────────────────────────────────────────
# Piece object – shared across branches (except when collapsed)
# ─────────────────────────────────────────────────────────────────────────────
class Piece:
    def __init__(self, kind: str, color: str):
        self.kind = kind             # 'K','Q','R','B','N','P'
        self.color = color           # 'white'/'black'
        self.moved = False           # for castling / pawn first move
        self.q_id = None             # None = classical; int tag = fuzzy set

    def char(self) -> str:
        return UNICODE[self.color][self.kind]


# ─────────────────────────────────────────────────────────────────────────────
# Board = list of *branches*, each branch is an 8×8 array of Piece|None
# ─────────────────────────────────────────────────────────────────────────────
class Board:
    def __init__(self):
        self.branches = [self._start_grid()]
        self.turn = "white"
        self.q_counter = 1           # next quantum-ID to tag superposed pieces

    @staticmethod
    def _start_grid():
        g = [[None] * 8 for _ in range(8)]
        order = ["R", "N", "B", "Q", "K", "B", "N", "R"]
        for c, k in enumerate(order):
            g[7][c] = Piece(k, "white")
            g[0][c] = Piece(k, "black")
            g[6][c] = Piece("P", "white")
            g[1][c] = Piece("P", "black")
        return g

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def inside(r, c):
        return 0 <= r < 8 and 0 <= c < 8

    # merged view – if every branch has *identical* piece here ➜ that piece,
    # else None (meaning "?" in the GUI)
    def merged_piece(self, r, c):
        first = self.branches[0][r][c]
        for b in self.branches[1:]:
            if (b[r][c] is None) != (first is None):
                return None
            if b[r][c] and (
                b[r][c].kind != first.kind or b[r][c].color != first.color
            ):
                return None
        return first

    # for move-generation we just inspect the *first* branch that contains the
    # piece at (r,c).  That is enough for highlighting.
    def piece_at_any_branch(self, r, c):
        for b in self.branches:
            p = b[r][c]
            if p:
                return p
        return None

    # ---------------------------------------------------------------- movement
    def classical_move(self, sr, sc, tr, tc):
        """Apply a classical move across *all* branches where legal."""
        new_branches = []
        for g in self.branches:
            p = g[sr][sc]
            if p and self._classical_legal(g, p, sr, sc, tr, tc):
                g2 = copy.deepcopy(g)
                g2[tr][tc] = g2[sr][sc]
                g2[sr][sc] = None
                g2[tr][tc].moved = True
                new_branches.append(g2)
            else:
                new_branches.append(copy.deepcopy(g))
        self.branches = new_branches
        self.turn = "black" if self.turn == "white" else "white"

    # simplified: only basic orthogonal / diagonal / knight / pawn moves
    def _classical_legal(self, grid, piece, sr, sc, tr, tc):
        if piece.kind == "K":  # kings stay classical, normal king move
            return max(abs(tr - sr), abs(tc - sc)) == 1
        if piece.kind == "N":
            return (abs(tr - sr), abs(tc - sc)) in [(2, 1), (1, 2)]
        if piece.kind == "B":
            return abs(tr - sr) == abs(tc - sc)
        if piece.kind == "R":
            return (sr == tr) ^ (sc == tc)
        if piece.kind == "Q":
            return abs(tr - sr) == abs(tc - sc) or (sr == tr) ^ (sc == tc)
        if piece.kind == "P":
            direction = -1 if piece.color == "white" else 1
            if tc == sc and tr - sr == direction and grid[tr][tc] is None:
                return True
        return False  # (castling, en-passant omitted for brevity)

    def quantum_move(self, sr, sc, t1r, t1c, t2r, t2c):
        """
        Remove every branch that doesn't have the moving piece on (sr,sc),
        then duplicate each surviving branch so the piece is on t1 and t2.
        """
        survivors = []
        for g in self.branches:
            if g[sr][sc]:
                survivors.append(g)
        if not survivors:
            return  # nothing to split

        tag = self.q_counter
        self.q_counter += 1
        new_branches = []
        for g in survivors:
            p = g[sr][sc]
            if p.kind == "K":
                continue  # kings can't quantum-move
            # branch 1
            g1 = copy.deepcopy(g)
            g1[t1r][t1c] = g1[sr][sc]
            g1[sr][sc] = None
            g1[t1r][t1c].q_id = tag
            new_branches.append(g1)
            # branch 2
            g2 = copy.deepcopy(g)
            g2[t2r][t2c] = g2[sr][sc]
            g2[sr][sc] = None
            g2[t2r][t2c].q_id = tag
            new_branches.append(g2)
        self.branches = new_branches
        self.turn = "black" if self.turn == "white" else "white"

    # ---------------------------------------------------------------- collapse
    def collapse_on(self, r, c, seed):
        """
        Observe square (r,c) with given RNG seed.  Remove every branch where
        that square *doesn't* contain a piece, then *randomly* choose one
        remaining branch.
        """
        branches = [b for b in self.branches if b[r][c]]
        if not branches:
            return False  # nothing there
        rng = random.Random(seed)
        chosen = rng.choice(branches)
        self.branches = [copy.deepcopy(chosen)]
        # tag cleared – collapsed pieces become classical
        for rr in range(8):
            for cc in range(8):
                p = self.branches[0][rr][cc]
                if p:
                    p.q_id = None
        return True


# ─────────────────────────────────────────────────────────────────────────────
# ChessGUI  (board-flip + quantum toggle + LAN sync)
# ─────────────────────────────────────────────────────────────────────────────
class ChessGUI:
    def __init__(self):
        self.board = Board()

        # --------------- Tk setup ---------------
        self.root = tk.Tk()
        self.root.title("LAN Quantum Chess")
        self.canvas = tk.Canvas(
            self.root, width=8 * SQUARE_SIZE, height=8 * SQUARE_SIZE
        )
        self.canvas.pack()
        self.chk_var = tk.BooleanVar()
        tk.Checkbutton(
            self.root, text="Q-move", variable=self.chk_var
        ).pack(anchor="w")
        self.status = tk.Label(self.root, font=("Arial", 12))
        self.status.pack()

        # --------------- network side -----------
        choice = simpledialog.askstring(
            "Network", "Type 'host' to host, or enter host-IP to join:"
        )
        if not choice:
            sys.exit(0)
        if choice.lower() == "host":
            self.is_host, self.color, self.opponent = True, "white", "black"
        else:
            self.is_host, self.host_ip = False, choice.strip()
            self.color, self.opponent = "black", "white"

        self.flip = self.color == "black"

        # --------------- click state ------------
        self.selected = None          # (r,c)
        self.q_first = None           # first target square for Q-move
        self.highlight = []
        self.sending = False

        self.canvas.bind("<Button-1>", self.on_click)
        self.draw()
        self.update_status()

        threading.Thread(target=self.net_loop, daemon=True).start()

    # ---------- board ↔ screen helpers ----------
    def rc(self, x, y):
        sr, sc = y // SQUARE_SIZE, x // SQUARE_SIZE
        return (7 - sr, 7 - sc) if self.flip else (sr, sc)

    def screen_square(self, br, bc):
        sr, sc = (7 - br, 7 - bc) if self.flip else (br, bc)
        return sc * SQUARE_SIZE, sr * SQUARE_SIZE

    # ---------- drawing -------------------------
    def draw(self):
        self.canvas.delete("all")
        light, dark = "#EEEED2", "#769656"
        for br in range(8):
            for bc in range(8):
                x0, y0 = self.screen_square(br, bc)
                self.canvas.create_rectangle(
                    x0,
                    y0,
                    x0 + SQUARE_SIZE,
                    y0 + SQUARE_SIZE,
                    fill=light if (br + bc) % 2 == 0 else dark,
                    outline="",
                )

        # highlights
        for br, bc in self.highlight:
            x0, y0 = self.screen_square(br, bc)
            self.canvas.create_rectangle(
                x0,
                y0,
                x0 + SQUARE_SIZE,
                y0 + SQUARE_SIZE,
                fill="yellow",
                stipple="gray25",
                outline="",
            )

        # pieces / ?
        for br in range(8):
            for bc in range(8):
                p = self.board.merged_piece(br, bc)
                glyph = "?" if p is None and any(
                    b[br][bc] for b in self.board.branches
                ) else (p.char() if p else None)
                if glyph:
                    x0, y0 = self.screen_square(br, bc)
                    self.canvas.create_text(
                        x0 + SQUARE_SIZE // 2,
                        y0 + SQUARE_SIZE // 2,
                        text=glyph,
                        font=("Arial", 36),
                    )

    def update_status(self):
        mode = "Q" if self.chk_var.get() else "C"
        self.status.config(
            text=f"You are {self.color}  |  Turn: {self.board.turn}  |  Mode: {mode}"
        )

    # ---------- algebraic helpers --------------
    def enc(self, r, c):
        return f"{FILES[c]}{8 - r}"

    def dec(self, s):
        return 8 - int(s[1]), FILES.index(s[0])

    # ---------- click handler ------------------
    def on_click(self, e):
        r, c = self.rc(e.x, e.y)
        p = self.board.piece_at_any_branch(r, c)

        if self.board.turn != self.color:
            return  # not our turn

        # ---------- Q-move flow ----------
        if self.chk_var.get():
            if self.selected is None:          # select piece first
                if p and p.color == self.color and p.kind != "K":
                    self.selected = (r, c)
                    self.highlight = self._legal_moves_rough(r, c)
            elif self.q_first is None:         # pick first target
                if (r, c) in self.highlight:
                    self.q_first = (r, c)
                    self.highlight = [
                        sq for sq in self.highlight if sq != (r, c)
                    ]
            else:                              # pick second target → commit
                if (r, c) in self.highlight:
                    sr, sc = self.selected
                    t1r, t1c = self.q_first
                    t2r, t2c = r, c
                    seed = random.randrange(2**32)
                    self.local_q_move(sr, sc, t1r, t1c, t2r, t2c, seed)
                    msg = f"Q:{self.enc(sr,sc)}{self.enc(t1r,t1c)}:{self.enc(sr,sc)}{self.enc(t2r,t2c)}:{seed}"
                    self.send_async(msg)
                    self._clear_selection()
        # -------- classical flow ----------
        else:
            if self.selected is None:
                if p and p.color == self.color:
                    self.selected = (r, c)
                    self.highlight = self._legal_moves_rough(r, c)
            else:
                if (r, c) in self.highlight:
                    sr, sc = self.selected
                    self.local_c_move(sr, sc, r, c)
                    msg = f"C:{self.enc(sr,sc)}{self.enc(r,c)}"
                    self.send_async(msg)
                    self._clear_selection()
                else:
                    self._clear_selection()

        self.draw()
        self.update_status()

    def _legal_moves_rough(self, r, c):
        # simplistic: any square inside board not holding our own classical king
        sqs = []
        for tr in range(8):
            for tc in range(8):
                if (tr, tc) != (r, c):
                    sqs.append((tr, tc))
        return sqs

    def _clear_selection(self):
        self.selected = None
        self.q_first = None
        self.highlight = []

    # ---------- local move helpers -------------
    def local_c_move(self, sr, sc, tr, tc):
        # collapse if target square fuzzy
        seed = random.randrange(2**32)
        self.board.collapse_on(tr, tc, seed)
        self.board.classical_move(sr, sc, tr, tc)

    def local_q_move(self, sr, sc, t1r, t1c, t2r, t2c, seed):
        # collapse origin square first if fuzzy
        self.board.collapse_on(sr, sc, seed)
        self.board.quantum_move(sr, sc, t1r, t1c, t2r, t2c)

    # ---------- networking ---------------------
    def send_async(self, msg_str):
        self.sending = True
        threading.Thread(
            target=self._send, args=(msg_str,), daemon=True
        ).start()

    def _send(self, s):
        try:
            if self.is_host:
                lan_socket.server_mode(s.encode(), "white")
            else:
                lan_socket.client_mode(s.encode(), "white", self.host_ip)
        finally:
            self.sending = False

    def recv_once(self):
        try:
            if self.is_host:
                return lan_socket.server_mode(b"", "black")
            else:
                return lan_socket.client_mode(b"", "black", self.host_ip)
        except Exception:
            return ""

       # ———————————————————————————————————————————
    # Apply one message that arrived over the LAN
    # ———————————————————————————————————————————
    def _apply_remote(self, msg: str):
        if msg.startswith("C:"):
            # classical  C:<src><dst>
            _, move = msg.split(":", 1)
            src, dst = move[:2], move[2:]
            sr, sc = self.dec(src)
            tr, tc = self.dec(dst)
            self.local_c_move(sr, sc, tr, tc)

        elif msg.startswith("Q:"):
            # quantum    Q:<src><t1>:<src><t2>:<seed>
            _, part1, part2, seed_str = msg.split(":")
            seed = int(seed_str)

            # decode squares
            sr, sc = self.dec(part1[:2])
            t1r, t1c = self.dec(part1[2:])
            t2r, t2c = self.dec(part2[2:])

            # reproduce local side’s collapse-then-split sequence
            self.board.collapse_on(sr, sc, seed)
            self.board.quantum_move(sr, sc, t1r, t1c, t2r, t2c)

        # one redraw & status update covers both cases
        self.draw()
        self.update_status()

    def net_loop(self):
        while True:
            if not self.sending and self.board.turn == self.opponent:
                msg = self.recv_once()
                if msg:
                    self.root.after(0, self._apply_remote, msg)
            time.sleep(0.1)

    # ---------- go! ----------------------------
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    ChessGUI().run()
