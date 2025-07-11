#download stockfish so the computer oppenent doesn't move randomly, change the path to where the stockfish file is
import os, shutil, random, copy, threading, time, sys, tkinter as tk
from tkinter import messagebox, simpledialog
import chess, chess.engine
import lan_socket

# ───────── Stockfish location ─────────
STOCKFISH_PATH = "stockfish.exe"  # <— adjust if needed

# fall-back if engine unreachable
if not (shutil.which(STOCKFISH_PATH) or os.path.isfile(STOCKFISH_PATH)):
    messagebox.showwarning(
        "Stockfish not found",
        "Stockfish engine was not found.\n"
        "AI will make random moves until you install / re-path it.")
    STOCKFISH_PATH = None

# ───────── UI constants ─────────
SQUARE_SIZE = 64
UNICODE = {
    "white": {"K":"♔","Q":"♕","R":"♖","B":"♗","N":"♘","P":"♙"},
    "black": {"K":"♚","Q":"♛","R":"♜","B":"♝","N":"♞","P":"♟"},
}
FILES = "abcdefgh"

# ───────── Piece ─────────
class Piece:
    def __init__(self, kind, color):
        self.kind = kind
        self.color = color
        self.moved = False
        self.q_id = None
    def char(self): return UNICODE[self.color][self.kind]

# ───────── Board (quantum) ─────────
class Board:
    def __init__(self):
        self.branches = [self._init_grid()]
        self.turn = "white"
        self._q_next = 1
    @staticmethod
    def _init_grid():
        g=[[None]*8 for _ in range(8)]
        row=["R","N","B","Q","K","B","N","R"]
        for c,k in enumerate(row):
            g[7][c]=Piece(k,"white"); g[0][c]=Piece(k,"black")
            g[6][c]=Piece("P","white"); g[1][c]=Piece("P","black")
        return g

    # ─ helpers ─
    def inside(self,r,c): return 0<=r<8 and 0<=c<8
    def piece_at_any(self,r,c):
        for b in self.branches:
            if b[r][c]: return b[r][c]
        return None
    def merged_piece(self,r,c):
        first=self.branches[0][r][c]
        for b in self.branches[1:]:
            if (b[r][c] is None)!=(first is None): return None
            if b[r][c] and (b[r][c].kind!=first.kind or b[r][c].color!=first.color):
                return None
        return first

    # ─ pattern-legal (path only) ─
    def _pattern_ok(self,g,p,sr,sc,tr,tc):
        if not self.inside(tr,tc): return False
        if g[tr][tc] and g[tr][tc].color==p.color: return False
        if p.kind=="K":   return max(abs(tr-sr),abs(tc-sc))==1
        if p.kind=="N":   return (abs(tr-sr),abs(tc-sc)) in [(2,1),(1,2)]
        if p.kind=="B":
            if abs(tr-sr)!=abs(tc-sc): return False
            dr=1 if tr>sr else -1; dc=1 if tc>sc else -1
            r,c=sr+dr,sc+dc
            while (r,c)!=(tr,tc):
                if g[r][c]: return False
                r+=dr; c+=dc
            return True
        if p.kind=="R":
            if sr!=tr and sc!=tc: return False
            if sr==tr:
                step=1 if tc>sc else -1
                for c in range(sc+step,tc,step):
                    if g[sr][c]: return False
            else:
                step=1 if tr>sr else -1
                for r in range(sr+step,tr,step):
                    if g[r][sc]: return False
            return True
        if p.kind=="Q":
            return self._pattern_ok(g,Piece("B",p.color),sr,sc,tr,tc) or \
                   self._pattern_ok(g,Piece("R",p.color),sr,sc,tr,tc)
        if p.kind=="P":
            dir_=-1 if p.color=="white" else 1
            start=6 if p.color=="white" else 1
            if tc==sc and g[tr][tc] is None:
                if tr-sr==dir_: return True
                if sr==start and tr-sr==2*dir_ and g[sr+dir_][sc] is None: return True
            if abs(tc-sc)==1 and tr-sr==dir_ and g[tr][tc] and g[tr][tc].color!=p.color:
                return True
        return False

    # ─ king safety helper ─
    def _king_in_check(self,g,color):
        # find king
        for r in range(8):
            for c in range(8):
                q=g[r][c]
                if q and q.kind=="K" and q.color==color:
                    kr,kc=r,c; break
        opp="black" if color=="white" else "white"
        for r in range(8):
            for c in range(8):
                q=g[r][c]
                if q and q.color==opp and self._pattern_ok(g,q,r,c,kr,kc):
                    return True
        return False

    # ─ full legal (pattern + king safety) ─
    def _legal(self,g,p,sr,sc,tr,tc):
        if not self._pattern_ok(g,p,sr,sc,tr,tc): return False
        sim=copy.deepcopy(g)
        sim[tr][tc], sim[sr][sc] = sim[sr][sc], None
        return not self._king_in_check(sim,p.color)

    # ─ classical / quantum moves ─
    def classical_move(self,sr,sc,tr,tc):
        nb=[]
        for g in self.branches:
            p=g[sr][sc]
            if p and self._legal(g,p,sr,sc,tr,tc):
                g2=copy.deepcopy(g)
                g2[tr][tc]=g2[sr][sc]; g2[sr][sc]=None; g2[tr][tc].moved=True
                nb.append(g2)
            else:
                nb.append(copy.deepcopy(g))
        self.branches=nb
        self.turn="black" if self.turn=="white" else "white"

    def quantum_move(self,sr,sc,t1r,t1c,t2r,t2c):
        survivors=[g for g in self.branches if g[sr][sc]]
        if not survivors: return
        tag=self._q_next; self._q_next+=1
        new=[]
        for g in survivors:
            p=g[sr][sc]
            if p.kind=="K": continue
            if self._legal(g,p,sr,sc,t1r,t1c):
                g1=copy.deepcopy(g); g1[t1r][t1c]=g1[sr][sc]; g1[sr][sc]=None; g1[t1r][t1c].q_id=tag; new.append(g1)
            if self._legal(g,p,sr,sc,t2r,t2c):
                g2=copy.deepcopy(g); g2[t2r][t2c]=g2[sr][sc]; g2[sr][sc]=None; g2[t2r][t2c].q_id=tag; new.append(g2)
        if new:
            self.branches=new
            self.turn="black" if self.turn=="white" else "white"

    # collapse
    def collapse_on(self,r,c,seed):
        br=[b for b in self.branches if b[r][c]]
        if not br: return False
        chosen=random.Random(seed).choice(br)
        self.branches=[copy.deepcopy(chosen)]
        for rr in range(8):
            for cc in range(8):
                p=self.branches[0][rr][cc]
                if p: p.q_id=None
        return True

    # Stockfish evaluation
    def _to_board(self,color):
        g=self.branches[0]
        kmap={"K":chess.KING,"Q":chess.QUEEN,"R":chess.ROOK,
              "B":chess.BISHOP,"N":chess.KNIGHT,"P":chess.PAWN}
        b=chess.Board(None)
        for r in range(8):
            for c in range(8):
                p=g[r][c]
                if p:
                    b.set_piece_at(chess.square(c,7-r),
                                    chess.Piece(kmap[p.kind],p.color=="white"))
        b.turn=(color=="white")
        return b

    def evaluate(self,color,samples=4,depth=12):
        if STOCKFISH_PATH is None:
            return random.uniform(-50,50)
        try:
            with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as eng:
                total=0
                for _ in range(samples):
                    tmp=copy.deepcopy(self)
                    for r in range(8):
                        for c in range(8):
                            if any(b[r][c] and b[r][c].q_id for b in tmp.branches):
                                tmp.collapse_on(r,c,random.randrange(2**32))
                    score=eng.analyse(tmp._to_board(color), chess.engine.Limit(depth=depth))["score"].white()
                    total+=score.score(mate_score=100000)
                return total/samples
        except chess.engine.EngineError:
            return random.uniform(-50,50)

    # stronger AI search
    def best_ai_move(self,color,max_q_samples=20):
        best_score=-1e9 if color=="white" else 1e9
        best=None

        # classical
        for r in range(8):
            for c in range(8):
                p=self.piece_at_any(r,c)
                if not(p and p.color==color): continue
                for tr in range(8):
                    for tc in range(8):
                        if self._legal(self.branches[0],p,r,c,tr,tc):
                            sim=copy.deepcopy(self); sim.classical_move(r,c,tr,tc)
                            sc=sim.evaluate(color,4,12)
                            if (color=="white" and sc>best_score) or (color=="black" and sc<best_score):
                                best_score=sc; best=("C",r,c,tr,tc)

        # quantum samples
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
            sim=copy.deepcopy(self); sim.collapse_on(r,c,seed)
            sim.quantum_move(r,c,*t1,*t2)
            sc=sim.evaluate(color,4,12)
            if (color=="white" and sc>best_score) or (color=="black" and sc<best_score):
                best_score=sc; best=("Q",r,c,*t1,*t2,seed)
            samples+=1
        return best

# ───────── GUI / Controller ─────────
class ChessGUI:
    def __init__(self):
        self.board=Board()

        # pick mode
        self.vs_ai=messagebox.askyesno("Opponent","Play against the computer?")
        if self.vs_ai:
            human_white=messagebox.askyesno("Colour","Play as White?")
            self.color="white" if human_white else "black"
            self.opponent="black" if human_white else "white"
            self.is_host=False
        else:
            choice=simpledialog.askstring("Network","Type 'host' to host, or enter host-IP to join:")
            if not choice: sys.exit(0)
            if choice.lower()=="host":
                self.is_host,self.color,self.opponent=True,"white","black"
            else:
                self.is_host,self.host_ip=False,choice.strip(),"black","white"
        self.flip=(self.color=="black")

        # widgets
        self.root=tk.Tk(); self.root.title("Quantum Chess")
        self.canvas=tk.Canvas(self.root,width=8*SQUARE_SIZE,height=8*SQUARE_SIZE); self.canvas.pack()
        self.chk=tk.BooleanVar(); tk.Checkbutton(self.root,text="Q-move",variable=self.chk).pack(anchor="w")
        self.status=tk.Label(self.root,font=("Arial",12)); self.status.pack()

        self.selected=None; self.q_first=None; self.highlight=[]
        self.sending=False

        self.canvas.bind("<Button-1>",self.click)
        self.draw(); self.status_update()
        threading.Thread(target=self.loop,daemon=True).start()

    # helpers
    def rc(self,x,y):
        sr,sc=y//SQUARE_SIZE,x//SQUARE_SIZE
        return (7-sr,7-sc) if self.flip else (sr,sc)
    def scr(self,r,c):
        sr,sc=(7-r,7-c) if self.flip else (r,c)
        return sc*SQUARE_SIZE, sr*SQUARE_SIZE
    def enc(self,r,c): return f"{FILES[c]}{8-r}"
    def dec(self,s):   return 8-int(s[1]), FILES.index(s[0])

    # draw
    def draw(self):
        self.canvas.delete("all")
        light,dark="#EEEED2","#769656"
        for r in range(8):
            for c in range(8):
                x0,y0=self.scr(r,c)
                self.canvas.create_rectangle(x0,y0,x0+SQUARE_SIZE,y0+SQUARE_SIZE,
                                             fill=light if (r+c)%2==0 else dark,outline="")
        for r,c in self.highlight:
            x0,y0=self.scr(r,c)
            self.canvas.create_rectangle(x0,y0,x0+SQUARE_SIZE,y0+SQUARE_SIZE,
                                         fill="yellow",stipple="gray25",outline="")
        for r in range(8):
            for c in range(8):
                glyph=None
                if any(b[r][c] for b in self.board.branches):
                    mp=self.board.merged_piece(r,c)
                    glyph=mp.char() if mp else "?"
                if glyph:
                    x0,y0=self.scr(r,c)
                    self.canvas.create_text(x0+SQUARE_SIZE//2,y0+SQUARE_SIZE//2,text=glyph,font=("Arial",36))

    def status_update(self):
        mode="Q" if self.chk.get() else "C"
        opp="AI" if self.vs_ai else "LAN"
        self.status.config(text=f"{self.color.capitalize()} | Turn:{self.board.turn} | {mode} | {opp}")

    # legal list
    def _moves(self,r,c):
        for g in self.board.branches:
            p=g[r][c]
            if p: return [(tr,tc) for tr in range(8) for tc in range(8)
                          if self.board._legal(g,p,r,c,tr,tc)]
        return []

    # click handler
    def click(self,e):
        r,c=self.rc(e.x,e.y)
        p=self.board.piece_at_any(r,c)
        if self.board.turn!=self.color: return

        if self.chk.get():  # Q-move
            if p and p.kind=="K": return
            if self.selected is None:
                if p and p.color==self.color:
                    self.selected=(r,c); self.highlight=self._moves(r,c)
            elif self.q_first is None:
                if (r,c) in self.highlight: self.q_first=(r,c)
            else:
                if (r,c) in self.highlight and (r,c)!=self.q_first:
                    sr,sc=self.selected; t1r,t1c=self.q_first; t2r,t2c=r,c
                    seed=random.randrange(2**32)
                    self.board.collapse_on(sr,sc,seed)
                    self.board.quantum_move(sr,sc,t1r,t1c,t2r,t2c)
                    if not self.vs_ai:
                        m=f"Q:{self.enc(sr,sc)}{self.enc(t1r,t1c)}:{self.enc(sr,sc)}{self.enc(t2r,t2c)}:{seed}"
                        self.send(m)
                    self.after()
                self.clear()
        else:  # classical
            if self.selected is None:
                if p and p.color==self.color:
                    self.selected=(r,c); self.highlight=self._moves(r,c)
            else:
                if (r,c) in self.highlight:
                    sr,sc=self.selected
                    self.board.collapse_on(r,c,random.randrange(2**32))
                    self.board.classical_move(sr,sc,r,c)
                    if not self.vs_ai:
                        self.send(f"C:{self.enc(sr,sc)}{self.enc(r,c)}")
                    self.after()
                self.clear()
        self.draw(); self.status_update()

    def clear(self):
        self.selected=self.q_first=None; self.highlight=[]

    def after(self):
        self.draw(); self.status_update()

    # networking
    def send(self,msg):
        if self.vs_ai: return
        self.sending=True
        def th():
            try:
                if self.is_host:
                    lan_socket.server_mode(msg.encode(),"white")
                else:
                    lan_socket.client_mode(msg.encode(),"white",self.host_ip)
            finally: self.sending=False
        threading.Thread(target=th,daemon=True).start()

    def recv(self):
        if self.is_host:
            return lan_socket.server_mode(b"","black")
        return lan_socket.client_mode(b"","black",self.host_ip)

    def apply_remote(self,msg):
        if msg.startswith("C:"):
            s,d=msg[2:4],msg[4:6]; sr,sc=self.dec(s); tr,tc=self.dec(d)
            self.board.collapse_on(tr,tc,random.randrange(2**32))
            self.board.classical_move(sr,sc,tr,tc)
        else:
            _,p1,p2,seed=msg.split(":"); seed=int(seed)
            sr,sc=self.dec(p1[:2]); t1r,t1c=self.dec(p1[2:]); t2r,t2c=self.dec(p2[2:])
            self.board.collapse_on(sr,sc,seed)
            self.board.quantum_move(sr,sc,t1r,t1c,t2r,t2c)
        self.after()

    # main loop
    def loop(self):
        while True:
            if self.vs_ai and self.board.turn==self.opponent:
                mv=self.board.best_ai_move(self.opponent)
                if mv[0]=="C":
                    _,sr,sc,tr,tc=mv
                    self.board.collapse_on(tr,tc,random.randrange(2**32))
                    self.board.classical_move(sr,sc,tr,tc)
                else:
                    _,sr,sc,t1r,t1c,t2r,t2c,seed=mv
                    self.board.collapse_on(sr,sc,seed)
                    self.board.quantum_move(sr,sc,t1r,t1c,t2r,t2c)
                self.after()
            elif not self.vs_ai and not self.sending and self.board.turn==self.opponent:
                m=self.recv()
                if m: self.root.after(0,self.apply_remote,m)
            time.sleep(0.1)

    def run(self): self.root.mainloop()

# ───────── entry ─────────
if __name__=="__main__":
    ChessGUI().run()
