import tkinter as tk
from tkinter import messagebox, simpledialog
import threading, time, sys, random, copy
import chess, chess.engine                    # NEW
import lan_socket

STOCKFISH_PATH = "stockfish"                  # <— change if needed
SQUARE_SIZE = 64
UNICODE = {
    "white": {"K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙"},
    "black": {"K": "♚", "Q": "♛", "R": "♜", "B": "♝", "N": "♞", "P": "♟"},
}
FILES = "abcdefgh"

# ─────────────────────────── Piece ───────────────────────────
class Piece:
    def __init__(self, kind: str, color: str):
        self.kind = kind
        self.color = color
        self.moved = False
        self.q_id = None           # None = classical, int = fuzzy tag
    def char(self):  return UNICODE[self.color][self.kind]

# ─────────────────────────── Board ───────────────────────────
class Board:
    """Quantum board = list of branches; each branch is an 8×8 grid."""

    def __init__(self):
        self.branches = [self._start_grid()]
        self.turn = "white"
        self.q_counter = 1

    @staticmethod
    def _start_grid():
        g = [[None]*8 for _ in range(8)]
        order = ["R","N","B","Q","K","B","N","R"]
        for c,k in enumerate(order):
            g[7][c] = Piece(k,"white")
            g[0][c] = Piece(k,"black")
            g[6][c] = Piece("P","white")
            g[1][c] = Piece("P","black")
        return g

    # ---------- helpers ----------
    def inside(self,r,c): return 0<=r<8 and 0<=c<8
    def merged_piece(self,r,c):
        first=self.branches[0][r][c]
        for b in self.branches[1:]:
            if (b[r][c] is None)!=(first is None): return None
            if b[r][c] and (b[r][c].kind!=first.kind or b[r][c].color!=first.color):
                return None
        return first
    def piece_at_any(self,r,c):
        for b in self.branches:
            if b[r][c]: return b[r][c]
        return None

    # ---------- classical legality (minimal but sufficient) ----------
    def _legal(self,g,p,sr,sc,tr,tc):
        if not self.inside(tr,tc): return False
        if g[tr][tc] and g[tr][tc].color==p.color: return False
        if p.kind=="K":
            return max(abs(tr-sr),abs(tc-sc))==1
        if p.kind=="N":
            return (abs(tr-sr),abs(tc-sc)) in [(2,1),(1,2)]
        if p.kind=="B":
            if abs(tr-sr)!=abs(tc-sc): return False
            dr = 1 if tr>sr else -1
            dc = 1 if tc>sc else -1
            r,c = sr+dr, sc+dc
            while (r,c)!=(tr,tc):
                if g[r][c]: return False
                r+=dr; c+=dc
            return True
        if p.kind=="R":
            if sr!=tr and sc!=tc: return False
            if sr==tr:
                step=1 if tc>sc else -1
                for c in range(sc+step, tc, step):
                    if g[sr][c]: return False
            else:
                step=1 if tr>sr else -1
                for r in range(sr+step, tr, step):
                    if g[r][sc]: return False
            return True
        if p.kind=="Q":
            return self._legal(g,Piece("B",p.color),sr,sc,tr,tc) or \
                   self._legal(g,Piece("R",p.color),sr,sc,tr,tc)
        if p.kind=="P":
            dir_= -1 if p.color=="white" else 1
            start=6 if p.color=="white" else 1
            if tc==sc and g[tr][tc] is None:
                if tr-sr==dir_: return True
                if sr==start and tr-sr==2*dir_ and g[sr+dir_][sc] is None: return True
            if abs(tc-sc)==1 and tr-sr==dir_ and g[tr][tc] and g[tr][tc].color!=p.color:
                return True
        return False

    # ---------- move application ----------
    def classical_move(self,sr,sc,tr,tc):
        nb=[]
        for g in self.branches:
            p=g[sr][sc]
            if p and self._legal(g,p,sr,sc,tr,tc):
                g2=copy.deepcopy(g)
                g2[tr][tc]=g2[sr][sc]; g2[sr][sc]=None
                g2[tr][tc].moved=True
                nb.append(g2)
            else:
                nb.append(copy.deepcopy(g))
        self.branches=nb
        self.turn = "black" if self.turn=="white" else "white"

    def quantum_move(self,sr,sc,t1r,t1c,t2r,t2c):
        surv=[g for g in self.branches if g[sr][sc]]
        if not surv: return
        tag=self.q_counter; self.q_counter+=1
        new=[]
        for g in surv:
            p=g[sr][sc]
            if p.kind=="K": continue
            if self._legal(g,p,sr,sc,t1r,t1c):
                g1=copy.deepcopy(g); g1[t1r][t1c]=g1[sr][sc]; g1[sr][sc]=None; g1[t1r][t1c].q_id=tag; new.append(g1)
            if self._legal(g,p,sr,sc,t2r,t2c):
                g2=copy.deepcopy(g); g2[t2r][t2c]=g2[sr][sc]; g2[sr][sc]=None; g2[t2r][t2c].q_id=tag; new.append(g2)
        if new:
            self.branches=new
            self.turn = "black" if self.turn=="white" else "white"

    # ---------- collapse ----------
    def collapse_on(self,r,c,seed):
        b=[br for br in self.branches if br[r][c]]
        if not b: return False
        chosen=random.Random(seed).choice(b)
        self.branches=[copy.deepcopy(chosen)]
        for rr in range(8):
            for cc in range(8):
                p=self.branches[0][rr][cc]
                if p: p.q_id=None
        return True

    # ---------- Stockfish evaluation ----------
    def _to_chess_board(self,color):
        g=self.branches[0]  # assume already collapsed
        pc={("white","K"):chess.KING, ("black","K"):chess.KING,
            ("white","Q"):chess.QUEEN,("black","Q"):chess.QUEEN,
            ("white","R"):chess.ROOK, ("black","R"):chess.ROOK,
            ("white","B"):chess.BISHOP,("black","B"):chess.BISHOP,
            ("white","N"):chess.KNIGHT,("black","N"):chess.KNIGHT,
            ("white","P"):chess.PAWN, ("black","P"):chess.PAWN}
        bb=chess.Board(None)
        for r in range(8):
            for c in range(8):
                p=g[r][c]
                if p:
                    sq=chess.square(c,7-r)
                    bb.set_piece_at(sq,chess.Piece(pc[(p.color,p.kind)],p.color=="white"))
        bb.turn = (color=="white")
        return bb

    def evaluate(self,color,samples=4,depth=10):
        with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as eng:
            total=0
            for _ in range(samples):
                tmp=copy.deepcopy(self)
                # collapse all fuzzy squares randomly
                for r in range(8):
                    for c in range(8):
                        if any(b[r][c] and b[r][c].q_id for b in tmp.branches):
                            tmp.collapse_on(r,c,random.randrange(2**32))
                board=tmp._to_chess_board(color)
                info=eng.analyse(board,chess.engine.Limit(depth=depth))
                sc=info["score"].white().score(mate_score=100000)
                total+=sc
            return total/samples

    # ---------- AI move search ----------
    def best_ai_move(self,color,max_q_samples=10):
        best=( -1e9 if color=="white" else 1e9, None )
        # classical
        for r in range(8):
            for c in range(8):
                p=self.piece_at_any(r,c)
                if not(p and p.color==color): continue
                for tr in range(8):
                    for tc in range(8):
                        if self._legal(self.branches[0],p,r,c,tr,tc):
                            sim=copy.deepcopy(self)
                            sim.classical_move(r,c,tr,tc)
                            sc=sim.evaluate(color,3,8)
                            if (color=="white" and sc>best[0]) or (color=="black" and sc<best[0]):
                                best=(sc,("C",r,c,tr,tc))
        # quantum (random samples)
        samples=0
        while samples<max_q_samples:
            r,c=random.randrange(8),random.randrange(8)
            p=self.piece_at_any(r,c)
            if not(p and p.color==color and p.kind!="K"): continue
            leg=[(tr,tc) for tr in range(8) for tc in range(8)
                 if self._legal(self.branches[0],p,r,c,tr,tc)]
            if len(leg)<2: continue
            t1,t2=random.sample(leg,2)
            seed=random.randrange(2**32)
            sim=copy.deepcopy(self)
            sim.collapse_on(r,c,seed)
            sim.quantum_move(r,c,*t1,*t2)
            sc=sim.evaluate(color,3,8)
            if (color=="white" and sc>best[0]) or (color=="black" and sc<best[0]):
                best=(sc,("Q",r,c,*t1,*t2,seed))
            samples+=1
        return best[1]

# ───────────────────────── GUI / Controller ─────────────────────────
class ChessGUI:
    def __init__(self):
        self.board=Board()

        # ----------- pick play-mode -----------
        self.vs_ai=messagebox.askyesno("Opponent","Play against the computer?")
        if self.vs_ai:
            human_white=messagebox.askyesno("Colour","Play as White?")
            self.color="white" if human_white else "black"
            self.opponent="black" if human_white else "white"
            self.is_host=False   # networking disabled
        else:
            # LAN setup
            choice=simpledialog.askstring("Network","Type 'host' to host, or enter host-IP to join:")
            if not choice: sys.exit(0)
            if choice.lower()=="host":
                self.is_host,self.color,self.opponent=True,"white","black"
            else:
                self.is_host,self.host_ip=False,choice.strip(),"black","white"

        self.flip=(self.color=="black")

        # ----------- Tk widgets -----------
        self.root=tk.Tk(); self.root.title("Quantum Chess")
        self.canvas=tk.Canvas(self.root,width=8*SQUARE_SIZE,height=8*SQUARE_SIZE)
        self.canvas.pack()
        self.chk_var=tk.BooleanVar(value=False)
        tk.Checkbutton(self.root,text="Q-move",variable=self.chk_var).pack(anchor="w")
        self.status=tk.Label(self.root,font=("Arial",12)); self.status.pack()

        # ----------- selection state -----------
        self.selected=None; self.q_first=None; self.highlight=[]
        self.sending=False

        self.canvas.bind("<Button-1>",self.on_click)
        self.draw(); self.update_status()

        threading.Thread(target=self.net_loop,daemon=True).start()

    # ---------- helpers ----------
    def rc(self,x,y):
        sr,sc=y//SQUARE_SIZE, x//SQUARE_SIZE
        return (7-sr,7-sc) if self.flip else (sr,sc)
    def screen_sq(self,br,bc):
        sr,sc=(7-br,7-bc) if self.flip else (br,bc)
        return sc*SQUARE_SIZE, sr*SQUARE_SIZE
    def enc(self,r,c): return f"{FILES[c]}{8-r}"
    def dec(self,s):   return 8-int(s[1]),FILES.index(s[0])

    # ---------- draw ----------
    def draw(self):
        self.canvas.delete("all")
        light,dark="#EEEED2","#769656"
        for r in range(8):
            for c in range(8):
                x0,y0=self.screen_sq(r,c)
                self.canvas.create_rectangle(x0,y0,x0+SQUARE_SIZE,y0+SQUARE_SIZE,
                                             fill=light if (r+c)%2==0 else dark,outline="")
        for r,c in self.highlight:
            x0,y0=self.screen_sq(r,c)
            self.canvas.create_rectangle(x0,y0,x0+SQUARE_SIZE,y0+SQUARE_SIZE,
                                         fill="yellow",stipple="gray25",outline="")
        for r in range(8):
            for c in range(8):
                glyph=None
                if any(b[r][c] for b in self.board.branches):
                    mp=self.board.merged_piece(r,c)
                    glyph=mp.char() if mp else "?"
                if glyph:
                    x0,y0=self.screen_sq(r,c)
                    self.canvas.create_text(x0+SQUARE_SIZE//2,y0+SQUARE_SIZE//2,
                                            text=glyph,font=("Arial",36))

    def update_status(self):
        mode="Q" if self.chk_var.get() else "C"
        opp="AI" if self.vs_ai else "LAN"
        self.status.config(text=f"{self.color.capitalize()} | Turn: {self.board.turn} | Mode:{mode} | vs {opp}")

    # ---------- move lists ----------
    def _legal_moves(self,r,c):
        for g in self.board.branches:
            p=g[r][c]
            if not p: continue
            return [(tr,tc) for tr in range(8) for tc in range(8) if self.board._legal(g,p,r,c,tr,tc)]
        return []

    # ---------- click ----------
    def on_click(self,e):
        r,c=self.rc(e.x,e.y)
        p=self.board.piece_at_any(r,c)
        if self.board.turn!=self.color: return
        if self.chk_var.get():   # Q-mode
            if p and p.kind=="K": return
            if self.selected is None:
                if p and p.color==self.color:
                    self.selected=(r,c); self.highlight=self._legal_moves(r,c)
            elif self.q_first is None:
                if (r,c) in self.highlight: self.q_first=(r,c)
            else:
                if (r,c) in self.highlight and (r,c)!=self.q_first:
                    sr,sc=self.selected; t1r,t1c=self.q_first; t2r,t2c=r,c
                    seed=random.randrange(2**32)
                    self.board.collapse_on(sr,sc,seed)
                    self.board.quantum_move(sr,sc,t1r,t1c,t2r,t2c)
                    if not self.vs_ai:  # send to peer
                        msg=f"Q:{self.enc(sr,sc)}{self.enc(t1r,t1c)}:{self.enc(sr,sc)}{self.enc(t2r,t2c)}:{seed}"
                        self.send_async(msg)
                    self.after_move()
                self._clear()
        else:                    # classical
            if self.selected is None:
                if p and p.color==self.color:
                    self.selected=(r,c); self.highlight=self._legal_moves(r,c)
            else:
                if (r,c) in self.highlight:
                    sr,sc=self.selected
                    self.board.collapse_on(r,c,random.randrange(2**32))
                    self.board.classical_move(sr,sc,r,c)
                    if not self.vs_ai:
                        self.send_async(f"C:{self.enc(sr,sc)}{self.enc(r,c)}")
                    self.after_move()
                self._clear()
        self.draw(); self.update_status()

    def _clear(self): self.selected=self.q_first=None; self.highlight=[]
    def after_move(self):
        self.draw(); self.update_status()

    # ---------- networking ----------
    def send_async(self,msg):
        if self.vs_ai: return
        self.sending=True
        threading.Thread(target=lambda:
            (lan_socket.server_mode if self.is_host else lan_socket.client_mode)(msg.encode(),"white",getattr(self,'host_ip','')) ,daemon=True).start()

    def recv_once(self):
        if self.is_host:
            return lan_socket.server_mode(b"","black")
        return lan_socket.client_mode(b"","black",self.host_ip)

    def _apply_remote(self,msg):
        if msg.startswith("C:"):
            _,mv=msg.split(":",1); s,d=mv[:2],mv[2:]; sr,sc=self.dec(s); tr,tc=self.dec(d)
            self.board.collapse_on(tr,tc,random.randrange(2**32))
            self.board.classical_move(sr,sc,tr,tc)
        else:  # Q
            _,p1,p2,seed=msg.split(":"); seed=int(seed)
            sr,sc=self.dec(p1[:2]); t1r,t1c=self.dec(p1[2:]); t2r,t2c=self.dec(p2[2:])
            self.board.collapse_on(sr,sc,seed)
            self.board.quantum_move(sr,sc,t1r,t1c,t2r,t2c)
        self.after_move()

    # ---------- main loop ----------
    def net_loop(self):
        while True:
            if self.vs_ai:
                if self.board.turn==self.opponent:
                    move=self.board.best_ai_move(self.opponent)
                    if move[0]=="C":
                        _,sr,sc,tr,tc=move
                        self.board.collapse_on(tr,tc,random.randrange(2**32))
                        self.board.classical_move(sr,sc,tr,tc)
                    else:
                        _,sr,sc,t1r,t1c,t2r,t2c,seed=move
                        self.board.collapse_on(sr,sc,seed)
                        self.board.quantum_move(sr,sc,t1r,t1c,t2r,t2c)
                    self.after_move()
            else:
                if not self.sending and self.board.turn==self.opponent:
                    msg=self.recv_once()
                    if msg: self.root.after(0,self._apply_remote,msg)
            time.sleep(0.1)

    # ---------- run ----------
    def run(self): self.root.mainloop()

# ────────────────────────────────
if __name__=="__main__":
    ChessGUI().run()
