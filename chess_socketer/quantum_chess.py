import tkinter as tk
from tkinter import messagebox, simpledialog
import threading, time, sys, random, copy
import lan_socket

# ─────────────────── constants ───────────────────
SQUARE_SIZE = 64
UNICODE = {
    "white": {"K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙"},
    "black": {"K": "♚", "Q": "♛", "R": "♜", "B": "♝", "N": "♞", "P": "♟"},
}
FILES = "abcdefgh"

# ─────────────────── data model ───────────────────
class Piece:
    def __init__(self, kind: str, color: str):
        self.kind = kind
        self.color = color
        self.moved = False
        self.q_id = None          # None → classical, int → fuzzy tag

    def char(self) -> str:
        return UNICODE[self.color][self.kind]


class Board:
    """A list of branches; each branch is an 8×8 Piece|None grid."""

    def __init__(self):
        self.branches = [self._start_grid()]
        self.turn = "white"
        self.q_counter = 1        # next tag for a new fuzzy pair

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

    # ── helpers ────────────────────────────────
    @staticmethod
    def inside(r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def merged_piece(self, r, c):
        """Return piece if *all* branches agree; else None (means '?')."""
        first = self.branches[0][r][c]
        for b in self.branches[1:]:
            if (b[r][c] is None) != (first is None):
                return None
            if b[r][c] and (
                b[r][c].kind != first.kind or b[r][c].color != first.color
            ):
                return None
        return first

    def piece_at_any_branch(self, r, c):
        for b in self.branches:
            if b[r][c]:
                return b[r][c]
        return None

    # ── chess legality (simplified) ────────────
    def _classical_legal(self, g, p, sr, sc, tr, tc):
        if not self.inside(tr, tc):
            return False
        if g[tr][tc] and g[tr][tc].color == p.color:
            return False
        if p.kind == "K":
            return max(abs(tr - sr), abs(tc - sc)) == 1
        if p.kind == "N":
            return (abs(tr - sr), abs(tc - sc)) in [(2, 1), (1, 2)]
        if p.kind == "B":
            if abs(tr - sr) != abs(tc - sc):
                return False
            step_r = 1 if tr > sr else -1
            step_c = 1 if tc > sc else -1
            r, c = sr + step_r, sc + step_c
            while (r, c) != (tr, tc):
                if g[r][c]:
                    return False
                r += step_r
                c += step_c
            return True
        if p.kind == "R":
            if sr != tr and sc != tc:
                return False
            if sr == tr:
                step = 1 if tc > sc else -1
                for c in range(sc + step, tc, step):
                    if g[sr][c]:
                        return False
            else:
                step = 1 if tr > sr else -1
                for r in range(sr + step, tr, step):
                    if g[r][sc]:
                        return False
            return True
        if p.kind == "Q":
            return self._classical_legal(g, Piece("B", p.color), sr, sc, tr, tc) or \
                   self._classical_legal(g, Piece("R", p.color), sr, sc, tr, tc)
        if p.kind == "P":
            direction = -1 if p.color == "white" else 1
            start_row = 6 if p.color == "white" else 1
            # forward
            if tc == sc and g[tr][tc] is None:
                if tr - sr == direction:
                    return True
                if sr == start_row and tr - sr == 2 * direction and g[sr + direction][sc] is None:
                    return True
            # capture
            if abs(tc - sc) == 1 and tr - sr == direction and g[tr][tc] and g[tr][tc].color != p.color:
                return True
        return False   # (no castling/en-passant/promo here for brevity)

    # ── apply moves ────────────────────────────
    def classical_move(self, sr, sc, tr, tc):
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

    def quantum_move(self, sr, sc, t1r, t1c, t2r, t2c):
        survivors = [g for g in self.branches if g[sr][sc]]
        if not survivors:
            return
        tag = self.q_counter
        self.q_counter += 1
        new = []
        for g in survivors:
            p = g[sr][sc]
            if p.kind == "K":         # kings can't quantum-move
                continue
            # branch 1
            if self._classical_legal(g, p, sr, sc, t1r, t1c):
                g1 = copy.deepcopy(g)
                g1[t1r][t1c] = g1[sr][sc]
                g1[sr][sc] = None
                g1[t1r][t1c].q_id = tag
                new.append(g1)
            # branch 2
            if self._classical_legal(g, p, sr, sc, t2r, t2c):
                g2 = copy.deepcopy(g)
                g2[t2r][t2c] = g2[sr][sc]
                g2[sr][sc] = None
                g2[t2r][t2c].q_id = tag
                new.append(g2)
        if new:
            self.branches = new
            self.turn = "black" if self.turn == "white" else "white"

    # ── collapse ───────────────────────────────
    def collapse_on(self, r, c, seed):
        branches = [b for b in self.branches if b[r][c]]
        if not branches:
            return False
        chosen = random.Random(seed).choice(branches)
        self.branches = [copy.deepcopy(chosen)]
        for rr in range(8):
            for cc in range(8):
                p = self.branches[0][rr][cc]
                if p:
                    p.q_id = None
        return True


# ─────────────────── GUI / controller ───────────────────
class ChessGUI:
    def __init__(self):
        self.board = Board()

        # ── Tk root & widgets ──────────────────
        self.root = tk.Tk()
        self.root.title("LAN Quantum Chess")
        self.canvas = tk.Canvas(self.root, width=8 * SQUARE_SIZE, height=8 * SQUARE_SIZE)
        self.canvas.pack()

        self.chk_var = tk.BooleanVar(value=False)   # OFF = classical, ON = quantum
        tk.Checkbutton(self.root, text="Q-move", variable=self.chk_var).pack(anchor="w")

        self.status = tk.Label(self.root, font=("Arial", 12))
        self.status.pack()

        # ── network side choice ─────────────────
        choice = simpledialog.askstring("Network", "Type 'host' to host, or enter host-IP to join:")
        if not choice:
            sys.exit(0)
        if choice.lower() == "host":
            self.is_host, self.color, self.opponent = True, "white", "black"
        else:
            self.is_host, self.host_ip = False, choice.strip()
            self.color, self.opponent = "black", "white"

        self.flip = self.color == "black"

        # ── selection state ─────────────────────
        self.selected = None          # (r,c)
        self.q_first = None           # first target for Q-move
        self.highlight = []
        self.sending = False

        self.canvas.bind("<Button-1>", self.on_click)
        self.draw()
        self.update_status()

        threading.Thread(target=self.net_loop, daemon=True).start()

    # ── board ↔ screen helpers ─────────────────
    def rc(self, x, y):
        sr, sc = y // SQUARE_SIZE, x // SQUARE_SIZE
        return (7 - sr, 7 - sc) if self.flip else (sr, sc)

    def screen_square(self, br, bc):
        sr, sc = (7 - br, 7 - bc) if self.flip else (br, bc)
        return sc * SQUARE_SIZE, sr * SQUARE_SIZE

    # ── drawing ────────────────────────────────
    def draw(self):
        self.canvas.delete("all")
        light, dark = "#EEEED2", "#769656"
        for br in range(8):
            for bc in range(8):
                x0, y0 = self.screen_square(br, bc)
                self.canvas.create_rectangle(
                    x0, y0, x0 + SQUARE_SIZE, y0 + SQUARE_SIZE,
                    fill=light if (br + bc) % 2 == 0 else dark, outline=""
                )

        # highlights
        for br, bc in self.highlight:
            x0, y0 = self.screen_square(br, bc)
            self.canvas.create_rectangle(
                x0, y0, x0 + SQUARE_SIZE, y0 + SQUARE_SIZE,
                fill="yellow", stipple="gray25", outline=""
            )

        # pieces / '?'
        for br in range(8):
            for bc in range(8):
                glyph = None
                if any(b[br][bc] for b in self.board.branches):
                    mp = self.board.merged_piece(br, bc)
                    glyph = mp.char() if mp else "?"
                if glyph:
                    x0, y0 = self.screen_square(br, bc)
                    self.canvas.create_text(
                        x0 + SQUARE_SIZE // 2, y0 + SQUARE_SIZE // 2,
                        text=glyph, font=("Arial", 36)
                    )

    def update_status(self):
        mode = "Q" if self.chk_var.get() else "C"
        self.status.config(text=f"You are {self.color}  |  Turn: {self.board.turn}  |  Mode: {mode}")

    # ── algebraic helpers ──────────────────────
    def enc(self, r, c):  return f"{FILES[c]}{8 - r}"
    def dec(self, s):     return 8 - int(s[1]), FILES.index(s[0])

    # ── legal moves generator ──────────────────
    def _legal_moves(self, r, c):
        for g in self.board.branches:
            p = g[r][c]
            if not p:
                continue
            moves = []
            for tr in range(8):
                for tc in range(8):
                    if self.board._classical_legal(g, p, r, c, tr, tc):
                        moves.append((tr, tc))
            return moves
        return []

    # ── click handler ──────────────────────────
    def on_click(self, e):
        r, c = self.rc(e.x, e.y)
        p = self.board.piece_at_any_branch(r, c)

        # block move if not our turn
        if self.board.turn != self.color:
            self._clear_selection()
            return

        # ——— QUANTUM mode ————————————————————
        if self.chk_var.get():
            if p and p.kind == "K":
                self._clear_selection()
                return

            if self.selected is None:                       # pick piece
                if p and p.color == self.color:
                    self.selected = (r, c)
                    self.highlight = self._legal_moves(r, c)

            elif self.q_first is None:                      # first target
                if (r, c) in self.highlight:
                    self.q_first = (r, c)
                else:
                    self._clear_selection()

            else:                                           # second target
                if (r, c) in self.highlight and (r, c) != self.q_first:
                    sr, sc = self.selected
                    t1r, t1c = self.q_first
                    t2r, t2c = r, c
                    seed = random.randrange(2**32)
                    self.local_q_move(sr, sc, t1r, t1c, t2r, t2c, seed)
                    msg = (
                        f"Q:{self.enc(sr,sc)}{self.enc(t1r,t1c)}:"
                        f"{self.enc(sr,sc)}{self.enc(t2r,t2c)}:{seed}"
                    )
                    self.send_async(msg)
                self._clear_selection()

        # ——— CLASSICAL mode ———————————————————
        else:
            if self.selected is None:                       # pick piece
                if p and p.color == self.color:
                    self.selected = (r, c)
                    self.highlight = self._legal_moves(r, c)

            else:                                           # choose target
                if (r, c) in self.highlight:
                    sr, sc = self.selected
                    self.local_c_move(sr, sc, r, c)
                    msg = f"C:{self.enc(sr,sc)}{self.enc(r,c)}"
                    self.send_async(msg)
                self._clear_selection()

        self.draw()
        self.update_status()

    def _clear_selection(self):
        self.selected = None
        self.q_first = None
        self.highlight = []

    # ── local move helpers ─────────────────────
    def local_c_move(self, sr, sc, tr, tc):
        seed = random.randrange(2**32)
        self.board.collapse_on(tr, tc, seed)
        self.board.classical_move(sr, sc, tr, tc)

    def local_q_move(self, sr, sc, t1r, t1c, t2r, t2c, seed):
        self.board.collapse_on(sr, sc, seed)
        self.board.quantum_move(sr, sc, t1r, t1c, t2r, t2c)

    # ── networking helpers ─────────────────────
    def send_async(self, msg_str):
        self.sending = True
        threading.Thread(target=self._send, args=(msg_str,), daemon=True).start()

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

    def _apply_remote(self, msg):
        if msg.startswith("C:"):
            _, move = msg.split(":", 1)
            src, dst = move[:2], move[2:]
            sr, sc = self.dec(src)
            tr, tc = self.dec(dst)
            self.local_c_move(sr, sc, tr, tc)

        elif msg.startswith("Q:"):
            _, part1, part2, seed_str = msg.split(":")
            seed = int(seed_str)
            sr, sc = self.dec(part1[:2])
            t1r, t1c = self.dec(part1[2:])
            t2r, t2c = self.dec(part2[2:])
            self.board.collapse_on(sr, sc, seed)
            self.board.quantum_move(sr, sc, t1r, t1c, t2r, t2c)

        self.draw()
        self.update_status()

    def net_loop(self):
        while True:
            if not self.sending and self.board.turn == self.opponent:
                msg = self.recv_once()
                if msg:
                    self.root.after(0, self._apply_remote, msg)
            time.sleep(0.1)

    # ── run ────────────────────────────────────
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    ChessGUI().run()
