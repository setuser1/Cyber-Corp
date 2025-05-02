import tkinter as tk
from tkinter import messagebox
import random

# Quantum Chess with full pieces, legal moves, and up to 2-position superposition
# Supports left-click to add superposition (max 2 positions) and right-click to collapse to that position
# Networking stubs for LAN extension

class QuantumPiece:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.positions = []  # superposed positions, up to 2

    def legal_moves(self, board):
        # Generate legal classical moves ignoring check/capture rules beyond bounds and occupancy
        dirs = []
        r, c = self.positions[0]
        moves = []
        if self.name == 'pawn':
            step = -1 if self.color == 'white' else 1
            for dc in [0]:
                nr, nc = r + step, c + dc
                if board.is_empty(nr, nc): moves.append((nr,nc))
        elif self.name == 'knight':
            offsets = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
            for dr,dc in offsets:
                nr,nc = r+dr, c+dc
                if board.is_on_board(nr,nc) and not board.is_friendly(nr,nc,self.color): moves.append((nr,nc))
        elif self.name == 'bishop': dirs = [(1,1),(1,-1),(-1,1),(-1,-1)]
        elif self.name == 'rook': dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        elif self.name == 'queen': dirs = [(1,1),(1,-1),(-1,1),(-1,-1),(1,0),(-1,0),(0,1),(0,-1)]
        elif self.name == 'king':
            for dr in [-1,0,1]:
                for dc in [-1,0,1]:
                    if dr==0 and dc==0: continue
                    nr,nc = r+dr, c+dc
                    if board.is_on_board(nr,nc) and not board.is_friendly(nr,nc,self.color): moves.append((nr,nc))
        # sliding for bishop/rook/queen
        if dirs:
            for dr,dc in dirs:
                nr, nc = r+dr, c+dc
                while board.is_on_board(nr,nc):
                    if board.is_empty(nr,nc):
                        moves.append((nr,nc))
                    elif board.is_enemy(nr,nc,self.color):
                        moves.append((nr,nc)); break
                    else:
                        break
                    nr += dr; nc += dc
        return moves

    def add_superposition(self, pos, board):
        if len(self.positions) >= 2:
            return False
        if pos in self.positions:
            return False
        if pos in self.legal_moves(board):
            self.positions.append(pos)
            return True
        return False

    def collapse(self, chosen_pos=None):
        if not self.positions:
            return None
        if chosen_pos and chosen_pos in self.positions:
            self.positions = [chosen_pos]
        else:
            self.positions = [random.choice(self.positions)]
        return self.positions[0]

class QuantumChessBoard(tk.Canvas):
    def __init__(self, parent, rows=8, cols=8, cell_size=64, *args, **kwargs):
        super().__init__(parent, width=cols*cell_size, height=rows*cell_size, *args, **kwargs)
        self.rows, self.cols, self.cell_size = rows, cols, cell_size
        self.pieces = []
        self.selected = None
        self.draw_board()
        self.bind("<Button-1>", self.on_left_click)
        self.bind("<Button-3>", self.on_right_click)

    def is_on_board(self, r, c): return 0 <= r < self.rows and 0 <= c < self.cols
    def is_empty(self, r, c): return all((r,c) not in p.positions for p in self.pieces)
    def is_friendly(self, r, c, color): return any((r,c) in p.positions and p.color==color for p in self.pieces)
    def is_enemy(self, r, c, color): return any((r,c) in p.positions and p.color!=color for p in self.pieces)

    def draw_board(self):
        self.delete("all")
        for r in range(self.rows):
            for c in range(self.cols):
                x1,y1 = c*self.cell_size, r*self.cell_size
                x2,y2 = x1+self.cell_size, y1+self.cell_size
                color = "white" if (r+c)%2 else "gray"
                self.create_rectangle(x1,y1,x2,y2, fill=color)
        self.draw_pieces()

    def draw_pieces(self):
        for p in self.pieces:
            for pos in p.positions:
                r,c = pos
                x,y = c*self.cell_size+self.cell_size//2, r*self.cell_size+self.cell_size//2
                symbol = p.name[0].upper() if p.color=='white' else p.name[0].lower()
                self.create_text(x,y, text=symbol, font=(None,24), tags="piece")

    def on_left_click(self, event):
        r,c = event.y//self.cell_size, event.x//self.cell_size
        # select piece
        for p in self.pieces:
            if (r,c) in p.positions:
                self.selected = p
                return
        # add superposition
        if self.selected:
            added = self.selected.add_superposition((r,c), self)
            if not added:
                messagebox.showinfo("Illegal Move", "Cannot superpose there.")
            self.selected = None
            self.draw_board()
            # send_move(self.selected)

    def on_right_click(self, event):
        r,c = event.y//self.cell_size, event.x//self.cell_size
        for p in self.pieces:
            if (r,c) in p.positions:
                p.collapse(chosen_pos=(r,c))
                self.draw_board()
                # send_move(p)
                return

class QuantumChessApp:
    def __init__(self):
        self.root = tk.Tk(); self.root.title("Quantum Chess")
        self.board = QuantumChessBoard(self.root)
        self.board.pack()
        self.setup_pieces()

    def setup_pieces(self):
        back = ['rook','knight','bishop','queen','king','bishop','knight','rook']
        # white
        for i,name in enumerate(back):
            p = QuantumPiece(name,'white'); p.positions=[(7,i)]; self.board.pieces.append(p)
        for i in range(8):
            p = QuantumPiece('pawn','white'); p.positions=[(6,i)]; self.board.pieces.append(p)
        # black
        for i,name in enumerate(back):
            p = QuantumPiece(name,'black'); p.positions=[(0,i)]; self.board.pieces.append(p)
        for i in range(8):
            p = QuantumPiece('pawn','black'); p.positions=[(1,i)]; self.board.pieces.append(p)
        self.board.draw_board()

    def run(self): self.root.mainloop()

if __name__=='__main__':
    QuantumChessApp().run()

# Networking stubs
# def send_move(piece):
#     pass
# def receive_move():
#     pass
