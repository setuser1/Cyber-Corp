import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import threading
import lan_socket  # Presumed corrected module with server_mode, client_mode, closing

# Quantum Chess with LAN room connect menu and random color assignment

class QuantumPiece:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.positions = []  # superposed positions, up to 2

    def legal_moves(self, board):
        dirs = []
        r, c = self.positions[0]
        moves = []
        if self.name == 'pawn':
            step = -1 if self.color == 'white' else 1
            start_row = 6 if self.color == 'white' else 1
            # One square
            nr, nc = r + step, c
            if board.is_on_board(nr, nc) and board.is_empty(nr, nc):
                moves.append((nr, nc))
                # Two squares
                nr2 = r + 2 * step
                if r == start_row and board.is_on_board(nr2, c) and board.is_empty(nr2, c):
                    moves.append((nr2, c))
        elif self.name == 'knight':
            offsets = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
            for dr, dc in offsets:
                nr, nc = r + dr, c + dc
                if board.is_on_board(nr, nc) and not board.is_friendly(nr, nc, self.color):
                    moves.append((nr, nc))
        elif self.name in ('bishop', 'rook', 'queen'):
            if self.name == 'bishop': dirs = [(1,1),(1,-1),(-1,1),(-1,-1)]
            if self.name == 'rook':   dirs = [(1,0),(-1,0),(0,1),(0,-1)]
            if self.name == 'queen':  dirs = [(1,1),(1,-1),(-1,1),(-1,-1),(1,0),(-1,0),(0,1),(0,-1)]
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                while board.is_on_board(nr, nc):
                    if board.is_empty(nr, nc):
                        moves.append((nr, nc))
                    elif board.is_enemy(nr, nc, self.color):
                        moves.append((nr, nc))
                        break
                    else:
                        break
                    nr += dr; nc += dc
        elif self.name == 'king':
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if board.is_on_board(nr, nc) and not board.is_friendly(nr, nc, self.color):
                        moves.append((nr, nc))
        return moves

    def add_superposition(self, pos, board):
        if len(self.positions) >= 2 or pos in self.positions:
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
    def __init__(self, parent, cell_size=64):
        super().__init__(parent, width=8*cell_size, height=8*cell_size)
        self.cell_size = cell_size
        self.pieces = []
        self.selected = None
        self.turn = None
        self.draw_board()
        self.bind("<Button-1>", self.on_left_click)
        self.bind("<Button-3>", self.on_right_click)

    def is_on_board(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def is_empty(self, r, c):
        return all((r, c) not in p.positions for p in self.pieces)

    def is_friendly(self, r, c, color):
        return any((r, c) in p.positions and p.color == color for p in self.pieces)

    def is_enemy(self, r, c, color):
        return any((r, c) in p.positions and p.color != color for p in self.pieces)

    def draw_board(self):
        self.delete("all")
        for r in range(8):
            for c in range(8):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                color = "white" if (r + c) % 2 else "gray"
                self.create_rectangle(x1, y1, x2, y2, fill=color)
        self.draw_pieces()

    def draw_pieces(self):
        self.delete("piece")
        for p in self.pieces:
            for (r, c) in p.positions:
                x = c * self.cell_size + self.cell_size // 2
                y = r * self.cell_size + self.cell_size // 2
                sym = p.name[0].upper() if p.color == 'white' else p.name[0].lower()
                self.create_text(x, y, text=sym, font=(None, 24), tags="piece")

    def on_left_click(self, event):
        r = event.y // self.cell_size
        c = event.x // self.cell_size
        for p in self.pieces:
            if (r, c) in p.positions and p.color == self.turn:
                self.selected = p
                return
        if self.selected:
            if not self.selected.add_superposition((r, c), self):
                messagebox.showinfo("Illegal Move", "Cannot superpose there.")
            self.selected = None
            self.draw_board()

    def on_right_click(self, event):
        r = event.y // self.cell_size
        c = event.x // self.cell_size
        for p in self.pieces:
            if (r, c) in p.positions and p.color == self.turn:
                old_pos = list(p.positions)[0]
                new_pos = p.collapse(chosen_pos=(r, c))
                self.draw_board()
                move_str = f"{old_pos}->{new_pos}"
                self.master.on_move_complete(move_str)
                return

class QuantumChessApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quantum Chess LAN")
        self.won = self.lost = self.draw = False
        self.mode = None
        self.color = None
        self.opponent_color = None

        # Menu
        menubar = tk.Menu(self.root)
        netmenu = tk.Menu(menubar, tearoff=0)
        netmenu.add_command(label="Host Game", command=self.host_game)
        netmenu.add_command(label="Join Game", command=self.join_game)
        menubar.add_cascade(label="Network", menu=netmenu)
        self.root.config(menu=menubar)

        # Status
        self.status = tk.Label(self.root, font=('Arial', 18))
        self.status.pack(pady=2)

        # Board
        self.board = QuantumChessBoard(self.root)
        self.board.pack()
        self.setup_pieces()

    def setup_pieces(self):
        self.board.pieces.clear()
        back = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        # White back row
        for i, name in enumerate(back):
            w = QuantumPiece(name, 'white')
            w.positions = [(7, i)]
            self.board.pieces.append(w)
        # White pawns
        for i in range(8):
            w = QuantumPiece('pawn', 'white')
            w.positions = [(6, i)]
            self.board.pieces.append(w)
        # Black back row
        for i, name in enumerate(back):
            b = QuantumPiece(name, 'black')
            b.positions = [(0, i)]
            self.board.pieces.append(b)
        # Black pawns
        for i in range(8):
            b = QuantumPiece('pawn', 'black')
            b.positions = [(1, i)]
            self.board.pieces.append(b)
        self.board.draw_board()

    def host_game(self):
        # Assign random color to host
        self.mode = 's'
        self.color = random.choice(['white', 'black'])
        self.opponent_color = 'black' if self.color == 'white' else 'white'
        self.board.turn = self.color
        messagebox.showinfo("Hosting", f"You are {self.color}. Opponent will be {self.opponent_color}.")
        # Send host color to client
        threading.Thread(target=lan_socket.server_mode, args=(None, self.color), daemon=True).start()
        self.update_status()

    def join_game(self):
        self.mode = 'c'
        ip = simpledialog.askstring("Join Game", "Server IP:", parent=self.root)
        self.server_ip = ip
        # Receive host color
        host_color = lan_socket.client_mode(None, None, ip)
        if host_color not in ('white', 'black'):
            messagebox.showerror("Error", "Failed to receive host color.")
            return
        self.opponent_color = host_color
        self.color = 'black' if host_color == 'white' else 'white'
        self.board.turn = host_color  # host starts
        messagebox.showinfo("Joined", f"Host is {host_color}. You are {self.color}.")
        # Start listening for moves
        threading.Thread(target=self.receive_moves, daemon=True).start()
        self.update_status()

    def update_status(self):
        mode_text = "Host" if self.mode == 's' else "Client" if self.mode == 'c' else ""
        self.status.config(text=f"{self.board.turn.capitalize()} to move [{mode_text}]")

    def on_move_complete(self, move_str):
        # Send move and/or receive opponent
        if self.mode == 's':
            opp = lan_socket.server_mode(move_str, self.color)
        else:
            opp = lan_socket.client_mode(move_str, self.color)
        # Switch turn
        self.board.turn = self.opponent_color
        self.update_status()
        # Apply opponent move immediately if returned
        if opp:
            # TODO: parse opp string and apply to board
            self.board.turn = self.color
            self.update_status()

    def receive_moves(self):
        while not (self.won or self.lost or self.draw):
            opp = lan_socket.client_mode(None, self.color)
            if opp:
                # TODO: apply opp
                self.board.turn = self.color
                self.update_status()

    def end_game(self, result):
        self.won = (result == self.color)
        self.lost = (result != self.color and result in ['white', 'black'])
        self.draw = (result == 'draw')
        messagebox.showinfo("Game Over", f"Result: {result}")
        lan_socket.closing(self.won, self.lost, self.draw)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    QuantumChessApp().run()
