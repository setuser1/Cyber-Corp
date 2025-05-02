import tkinter as tk
import random

# Unicode characters for chess pieces
WHITE_KING = '\u2654'
WHITE_QUEEN = '\u2655'
WHITE_ROOK = '\u2656'
WHITE_BISHOP = '\u2657'
WHITE_KNIGHT = '\u2658'
WHITE_PAWN = '\u2659'

BLACK_KING = '\u265A'
BLACK_QUEEN = '\u265B'
BLACK_ROOK = '\u265C'
BLACK_BISHOP = '\u265D'
BLACK_KNIGHT = '\u265E'
BLACK_PAWN = '\u265F'

class ChessApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter Chess")
        self.board_frame = tk.Frame(self)
        self.board_frame.pack()

        # 8x8 board state: each cell holds piece character or None
        self.board = [[None for _ in range(8)] for _ in range(8)]

        # Randomly decide who plays first
        self.turn = random.choice(['white', 'black'])
        self.status_label = tk.Label(self, text=f"{self.turn.capitalize()} to move", font=('Arial', 14))
        self.status_label.pack(pady=5)

        # Track drag data
        self.drag_data = {'widget': None, 'r0': None, 'c0': None, 'piece': None}

        self.squares = {}  # (row, col) -> label widget
        self._create_board_ui()
        self._setup_pieces()

        # Buffers for socket moves
        self.last_sent_move = None
        self.last_received_move = None

    def _create_board_ui(self):
        for row in range(8):
            for col in range(8):
                square_color = '#F0D9B5' if (row + col) % 2 == 0 else '#B58863'
                lbl = tk.Label(
                    self.board_frame,
                    text=' ',
                    font=('Arial', 32),
                    width=2,
                    height=1,
                    bg=square_color
                )
                lbl.grid(row=row, column=col)
                lbl.bind('<ButtonPress-1>', lambda e, r=row, c=col: self.on_drag_start(e, r, c))
                lbl.bind('<B1-Motion>', self.on_drag_motion)
                lbl.bind('<ButtonRelease-1>', self.on_drag_release)
                self.squares[(row, col)] = lbl

    def _setup_pieces(self):
        # Setup pawns
        for col in range(8):
            self.board[1][col] = WHITE_PAWN
            self.board[6][col] = BLACK_PAWN
        # Rooks
        self.board[0][0] = self.board[0][7] = WHITE_ROOK
        self.board[7][0] = self.board[7][7] = BLACK_ROOK
        # Knights
        self.board[0][1] = self.board[0][6] = WHITE_KNIGHT
        self.board[7][1] = self.board[7][6] = BLACK_KNIGHT
        # Bishops
        self.board[0][2] = self.board[0][5] = WHITE_BISHOP
        self.board[7][2] = self.board[7][5] = BLACK_BISHOP
        # Queens
        self.board[0][3] = WHITE_QUEEN
        self.board[7][3] = BLACK_QUEEN
        # Kings
        self.board[0][4] = WHITE_KING
        self.board[7][4] = BLACK_KING

        self._redraw_board()

    def _redraw_board(self):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                lbl = self.squares[(row, col)]
                lbl['text'] = piece if piece else ' '

    def on_drag_start(self, event, row, col):
        piece = self.board[row][col]
        if piece and self._piece_color(piece) == self.turn:
            widget = event.widget
            self.drag_data['piece'] = piece
            self.drag_data['r0'] = row
            self.drag_data['c0'] = col
            # Create floating widget
            drag_lbl = tk.Label(self.board_frame, text=piece, font=('Arial', 32))
            drag_lbl.place(x=event.x, y=event.y)
            self.drag_data['widget'] = drag_lbl
            # Remove original
            self.board[row][col] = None
            widget['text'] = ' '

    def on_drag_motion(self, event):
        drag_lbl = self.drag_data.get('widget')
        if drag_lbl:
            # update position relative to board_frame
            x = event.x_root - self.board_frame.winfo_rootx() - 20
            y = event.y_root - self.board_frame.winfo_rooty() - 20
            drag_lbl.place(x=x, y=y)

    def on_drag_release(self, event):
        drag_lbl = self.drag_data.get('widget')
        if not drag_lbl:
            return
        # Determine target square
        x_rel = event.x_root - self.board_frame.winfo_rootx()
        y_rel = event.y_root - self.board_frame.winfo_rooty()
        lbl_w = self.squares[(0,0)].winfo_width()
        lbl_h = self.squares[(0,0)].winfo_height()
        c1 = min(max(int(x_rel / lbl_w), 0), 7)
        r1 = min(max(int(y_rel / lbl_h), 0), 7)

        r0, c0 = self.drag_data['r0'], self.drag_data['c0']
        piece = self.drag_data['piece']
        move_str = self._coords_to_move(r0, c0, r1, c1)
        if self._is_valid_move(r0, c0, r1, c1):
            self.board[r1][c1] = piece
            self._redraw_board()
            self.last_sent_move = move_str
            self.send_move(move_str)
            self.turn = 'black' if self.turn == 'white' else 'white'
            self.status_label['text'] = f"{self.turn.capitalize()} to move"
        else:
            # Revert
            self.board[r0][c0] = piece
            self.squares[(r0, c0)]['text'] = piece

        drag_lbl.destroy()
        self.drag_data = {'widget': None, 'r0': None, 'c0': None, 'piece': None}

    def _is_valid_move(self, r0, c0, r1, c1):
        piece = self.board[r1][c1]
        # Block capturing own
        if piece and self._piece_color(piece) == self.turn:
            return False
        return True  # full rules omitted

    def _coords_to_move(self, r0, c0, r1, c1):
        cols = 'abcdefgh'
        return f"{cols[c0]}{8-r0}{cols[c1]}{8-r1}"

    def _piece_color(self, piece):
        return 'white' if piece in (WHITE_KING, WHITE_QUEEN, WHITE_ROOK,
                                     WHITE_BISHOP, WHITE_KNIGHT, WHITE_PAWN) else 'black'

    # Placeholder socket methods
    def send_move(self, move_str):
        print(f"Sending move: {move_str}")

    def on_move_received(self, move_str):
        self.last_received_move = move_str
        cols = 'abcdefgh'
        c0 = cols.index(move_str[0])
        r0 = 8 - int(move_str[1])
        c1 = cols.index(move_str[2])
        r1 = 8 - int(move_str[3])
        if self._is_valid_move(r0, c0, r1, c1):
            self.board[r1][c1] = self.board[r0][c0]
            self.board[r0][c0] = None
            self._redraw_board()
            self.turn = 'black' if self.turn == 'white' else 'white'
            self.status_label['text'] = f"{self.turn.capitalize()} to move"

if __name__ == '__main__':
    app = ChessApp()
    app.mainloop()
