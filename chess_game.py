import copy

class ChessBoard:
    def __init__(self):
        self.board = self.init_board()
        self.turn = 'w'  # 'w' for white, 'b' for black
        self.castling = {'w': {'K': True, 'Q': True}, 'b': {'K': True, 'Q': True}}
        self.en_passant = None
        self.halfmove = 0
        self.fullmove = 1

    def init_board(self):
        board = [['' for _ in range(8)] for _ in range(8)]
        board[0] = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
        board[1] = ['p'] * 8
        board[6] = ['P'] * 8
        board[7] = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        return board

    def print_board(self):
        print('  a b c d e f g h')
        for i in range(8):
            print(f"{8-i} {' '.join(self.board[i] if self.board[i] else '.')} {8-i}")
        print('  a b c d e f g h')
        print()

    def get_piece(self, pos):
        r, c = pos
        return self.board[r][c]

    def set_piece(self, pos, piece):
        r, c = pos
        self.board[r][c] = piece

    def is_empty(self, pos):
        return self.get_piece(pos) == ''

    def is_enemy(self, pos, color):
        piece = self.get_piece(pos)
        return piece and piece.isupper() != color

    def is_own(self, pos, color):
        piece = self.get_piece(pos)
        return piece and piece.isupper() == color

    def in_bounds(self, pos):
        r, c = pos
        return 0 <= r < 8 and 0 <= c < 8

    def get_moves(self, pos):
        piece = self.get_piece(pos)
        if not piece:
            return []
        color = piece.isupper()  # True for white
        piece_type = piece.upper()
        moves = []
        r, c = pos
        if piece_type == 'P':
            dir = -1 if color else 1
            start_row = 6 if color else 1
            # Forward
            if self.in_bounds((r + dir, c)) and self.is_empty((r + dir, c)):
                moves.append((r + dir, c))
                if r == start_row and self.in_bounds((r + 2*dir, c)) and self.is_empty((r + 2*dir, c)):
                    moves.append((r + 2*dir, c))
            # Captures
            for dc in [-1, 1]:
                cap_pos = (r + dir, c + dc)
                if self.in_bounds(cap_pos) and (self.is_enemy(cap_pos, color) or cap_pos == self.en_passant):
                    moves.append(cap_pos)
        elif piece_type in ['R', 'B', 'Q']:
            directions = {
                'R': [(-1, 0), (1, 0), (0, -1), (0, 1)],
                'B': [(-1, -1), (-1, 1), (1, -1), (1, 1)],
                'Q': [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
            }
            for dr, dc in directions[piece_type]:
                nr, nc = r + dr, c + dc
                while self.in_bounds((nr, nc)):
                    if self.is_empty((nr, nc)):
                        moves.append((nr, nc))
                    elif self.is_enemy((nr, nc), color):
                        moves.append((nr, nc))
                        break
                    else:
                        break
                    nr += dr
                    nc += dc
        elif piece_type == 'N':
            for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
                nr, nc = r + dr, c + dc
                if self.in_bounds((nr, nc)) and not self.is_own((nr, nc), color):
                    moves.append((nr, nc))
        elif piece_type == 'K':
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nr, nc = r + dr, c + dc
                if self.in_bounds((nr, nc)) and not self.is_own((nr, nc), color):
                    moves.append((nr, nc))
            # Castling
            if color and self.castling['w']['K'] and all(self.is_empty((7, i)) for i in [5,6]) and not self.is_attacked((7,4), False) and not self.is_attacked((7,5), False) and not self.is_attacked((7,6), False):
                moves.append((7,6))
            if color and self.castling['w']['Q'] and all(self.is_empty((7, i)) for i in [1,2,3]) and not self.is_attacked((7,4), False) and not self.is_attacked((7,3), False) and not self.is_attacked((7,2), False):
                moves.append((7,2))
            if not color and self.castling['b']['K'] and all(self.is_empty((0, i)) for i in [5,6]) and not self.is_attacked((0,4), True) and not self.is_attacked((0,5), True) and not self.is_attacked((0,6), True):
                moves.append((0,6))
            if not color and self.castling['b']['Q'] and all(self.is_empty((0, i)) for i in [1,2,3]) and not self.is_attacked((0,4), True) and not self.is_attacked((0,3), True) and not self.is_attacked((0,2), True):
                moves.append((0,2))
        return moves

    def is_attacked(self, pos, by_color):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.isupper() == by_color:
                    if pos in self.get_moves((r, c)):
                        return True
        return False

    def make_move(self, start, end):
        piece = self.get_piece(start)
        captured = self.get_piece(end)
        self.set_piece(end, piece)
        self.set_piece(start, '')
        color = piece.isupper()
        # Handle special moves
        if piece.upper() == 'P':
            if abs(start[0] - end[0]) == 2:
                self.en_passant = ((start[0] + end[0]) // 2, start[1])
            elif end == self.en_passant:
                # En passant capture
                self.set_piece((start[0], end[1]), '')
            elif end[0] == (0 if not color else 7):
                # Promotion, promote to queen
                self.set_piece(end, 'Q' if color else 'q')
        elif piece.upper() == 'K':
            if abs(start[1] - end[1]) == 2:
                # Castling
                if end[1] == 6:
                    rook_pos = (end[0], 7)
                    rook_end = (end[0], 5)
                    self.set_piece(rook_end, self.get_piece(rook_pos))
                    self.set_piece(rook_pos, '')
                elif end[1] == 2:
                    rook_pos = (end[0], 0)
                    rook_end = (end[0], 3)
                    self.set_piece(rook_end, self.get_piece(rook_pos))
                    self.set_piece(rook_pos, '')
            # Update castling rights
            if color:
                self.castling['w']['K'] = False
                self.castling['w']['Q'] = False
            else:
                self.castling['b']['K'] = False
                self.castling['b']['Q'] = False
        elif piece.upper() == 'R':
            if start == (7,0):
                self.castling['w']['Q'] = False
            elif start == (7,7):
                self.castling['w']['K'] = False
            elif start == (0,0):
                self.castling['b']['Q'] = False
            elif start == (0,7):
                self.castling['b']['K'] = False
        self.en_passant = None
        self.halfmove += 1
        if piece.upper() == 'P' or captured:
            self.halfmove = 0
        if not color:
            self.fullmove += 1
        self.turn = 'b' if self.turn == 'w' else 'w'

    def is_check(self, color):
        king_pos = None
        king = 'K' if color == 'w' else 'k'
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == king:
                    king_pos = (r, c)
                    break
        if not king_pos:
            return False
        enemy_color = not (color == 'w')
        return self.is_attacked(king_pos, enemy_color)

    def is_checkmate(self, color):
        if not self.is_check(color):
            return False
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.isupper() == (color == 'w'):
                    moves = self.get_moves((r, c))
                    for move in moves:
                        temp_board = copy.deepcopy(self)
                        temp_board.make_move((r, c), move)
                        if not temp_board.is_check(color):
                            return False
        return True

    def is_stalemate(self, color):
        if self.is_check(color):
            return False
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.isupper() == (color == 'w'):
                    moves = self.get_moves((r, c))
                    for move in moves:
                        temp_board = copy.deepcopy(self)
                        temp_board.make_move((r, c), move)
                        if not temp_board.is_check(color):
                            return False
        return True

def parse_move(move_str):
    if len(move_str) != 4:
        return None
    try:
        start_col = ord(move_str[0].lower()) - ord('a')
        start_row = 8 - int(move_str[1])
        end_col = ord(move_str[2].lower()) - ord('a')
        end_row = 8 - int(move_str[3])
        if not all(0 <= x < 8 for x in [start_col, start_row, end_col, end_row]):
            return None
        return (start_row, start_col), (end_row, end_col)
    except:
        return None

def main():
    game = ChessBoard()
    import random
    while True:
        game.print_board()
        if game.is_checkmate(game.turn):
            winner = 'White' if game.turn == 'b' else 'Black'
            print(f"Checkmate! {winner} wins!")
            break
        if game.is_stalemate(game.turn):
            print("Stalemate! It's a draw.")
            break
        if game.turn == 'b':
            # Computer move for black
            possible_moves = []
            for r in range(8):
                for c in range(8):
                    piece = game.board[r][c]
                    if piece and piece.isupper() == (game.turn == 'w'):
                        moves = game.get_moves((r, c))
                        for move in moves:
                            temp_board = copy.deepcopy(game)
                            temp_board.make_move((r, c), move)
                            if not temp_board.is_check(game.turn):
                                possible_moves.append(((r, c), move))
            if possible_moves:
                start, end = random.choice(possible_moves)
                game.make_move(start, end)
                move_notation = f"{chr(start[1] + ord('a'))}{8-start[0]}{chr(end[1] + ord('a'))}{8-end[0]}"
                print(f"Computer plays: {move_notation}")
            else:
                print("No legal moves for computer.")
                break
        else:
            move_str = input(f"{'White'}'s turn (e.g., e2e4): ")
            move = parse_move(move_str)
            if not move:
                print("Invalid move format. Use algebraic notation like e2e4.")
                continue
            start, end = move
            piece = game.get_piece(start)
            if not piece or piece.isupper() != (game.turn == 'w'):
                print("No piece there or not your turn.")
                continue
            if end not in game.get_moves(start):
                print("Invalid move.")
                continue
            game.make_move(start, end)

if __name__ == "__main__":
    main()