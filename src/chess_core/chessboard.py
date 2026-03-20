from src.chess_core.shapes import King, Figure, Rook, Pawn, Knight, Queen, Bishop

from src.enums import MoveResult, PieceColor
from src.dataclass import MoveRecord, CastlingRights
from typing import Optional



class ChessBoard:
    def __init__(self):
        self.rows = 8
        self.cols = 8

        self.kings: dict[PieceColor, King] = {}
        self._board = [[0 for _ in range(self.rows)] for _ in range(self.cols)]

        self.castling_rights: CastlingRights = CastlingRights()
        self.en_passant_target: Optional[tuple[int, int]] = None



    def get_board(self):
        return self._board


    def add_figure(self, *, x: int, y: int, figure) -> MoveResult:
        if not self._board[y][x]: #If cell is empty

            self._board[y][x] = figure

            if isinstance(figure, King):
                self.kings[figure.color] = figure
            return MoveResult.OK

        return MoveResult.CELL_OCCUPIED


    def get_figures(self) -> list[Figure]:
        figures = []
        for y in self._board:
            for x in y:
                if not x == 0:
                    figures.append(x)
        return figures


    def apply_move(self, move: MoveRecord):
        # Correct work by
        # promotion +
        # capture +
        # simple move +
        # castle +
        # en_passant +
        from_x, from_y = move.from_pos
        to_x, to_y = move.to_pos

        piece: Figure = move.piece

        if move.captured_piece:
            capture_x, capture_y = move.captured_pos
            self._board[capture_y][capture_x] = 0

        self._board[to_y][to_x] = piece
        self._board[from_y][from_x] = 0

        piece.cord = move.to_pos

        self.change_castling_rights(move) # has bug auto change castling_rights



        if move.rook:
            rook = move.rook
            rook_from_x, rook_from_y = move.rook_from
            rook_to_x, rook_to_y = move.rook_to

            self._board[rook_from_y][rook_from_x] = 0
            self._board[rook_to_y][rook_to_x] = rook

            rook.cord = (rook_to_x, rook_to_y)

        last_line = 7 if move.piece.color == PieceColor.WHITE else 0
        if move.promotion_pawn:

            self._board[to_y][to_x] = move.promotion_pawn


        elif isinstance(move.piece, Pawn) and to_y == last_line:
            self._board[to_y][to_x] = 0






    def undo(self, move: MoveRecord):
        # Correct work when
        # promotion +
        # capture +
        # simple move +
        # castle +
        # en_passant +
        # If move is promotion + capture ? To my mind -
        from_x, from_y = move.from_pos
        to_x, to_y = move.to_pos

        piece: Figure = move.piece


        self._board[from_y][from_x] = piece

        if move.captured_piece is None:
            self._board[to_y][to_x] = 0
        else:
            cx, cy = move.captured_pos
            self._board[cy][cx] = move.captured_piece

        if move.rook:
            rook = move.rook
            rook_from_x, rook_from_y = move.rook_from
            rook_to_x, rook_to_y = move.rook_to

            self._board[rook_to_y][rook_to_x] = 0
            self._board[rook_from_y][rook_from_x] = rook

            rook.cord = (rook_from_x, rook_from_y)

        piece.cord = move.from_pos

        self.castling_rights = move.prev_castling_rights
        self.en_passant_target = move.prev_en_passant


    def change_castling_rights(self, record: MoveRecord):
        piece = record.piece
        from_x, from_y = record.from_pos
        to_x, to_y = record.to_pos
        color = record.piece.color


        if isinstance(record.piece, Rook):

            if from_x == 0 and self.castling_rights.can_castle_kingside(color):
                if color == PieceColor.WHITE:
                    self.castling_rights.white_king_side = False

                if color == PieceColor.BLACK:
                    self.castling_rights.black_king_side = False

            if from_x == 7 and self.castling_rights.can_castle_queenside(color):
                if color == PieceColor.WHITE:
                    self.castling_rights.white_queen_side = False

                if color == PieceColor.BLACK:
                    self.castling_rights.black_queen_side = False


        if isinstance(piece, King):
            if color == PieceColor.WHITE:
                self.castling_rights.white_king_side = False
                self.castling_rights.white_queen_side = False

            elif color == PieceColor.BLACK:
                self.castling_rights.black_king_side = False
                self.castling_rights.black_queen_side = False

        dif = abs(from_y - to_y)
        if isinstance(piece, Pawn) and dif == 2:
            self.en_passant_target = (from_x, int((from_y + to_y) / 2))

        else:
            self.en_passant_target = None


    def get_piece(self, *, cord: tuple[int, int]) -> Figure:
        x, y = cord
        return self._board[y][x]


    def is_empty(self, x: int, y: int) -> bool:
        piece = self._board[y][x]
        return piece == 0


    def is_inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.rows and 0 <= y < self.cols


    def king_is_check(self, color: PieceColor):

        kx, ky = self.find_king(color=color)
        enemy = color.opposite()

        return self.is_square_attacked(enemy=enemy, x=kx, y=ky)


    def is_square_attacked(self, x, y, enemy):
        ray_attack = {
            (Rook, Queen): [
                (1, 0), (0, 1), (-1, 0), (0, -1)
            ],
            (Bishop, Queen) : [
                (1, 1), (1, -1), (-1, 1), (-1, -1)
            ]
        }
        single_attack = {
            King: [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],

            Knight: [(-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2), (-2, -1), (-2, 1)]
        }

        for ex, deltas in ray_attack.items():
            if self.ray_attack(
                    x=x,
                    y=y,
                    enemy_color=enemy,
                    expected_types=ex,
                    deltas=deltas
            ):
                return True

        for ex, deltas in single_attack.items():
            if self.single_attack(
                    x=x,
                    y=y,
                    enemy_color=enemy,
                    expected_types=ex,
                    deltas=deltas
            ):
                return True

        direction = -1 if enemy == PieceColor.WHITE else 1

        for dx in (-1, 1):
            if self.has_piece(x + dx, y - direction, Pawn, enemy):
                return True

        return False


    def has_piece(self, x: int, y: int, piece_type: type, color: PieceColor) -> bool:
        if not self.is_inside(x, y): # If x, y not in the board
            return False

        piece = self._board[y][x]
        if piece == 0:
            return False

        return isinstance(piece, piece_type) and piece.color == color


    def ray_attack(self, enemy_color, expected_types, deltas, x, y):
        deltas = deltas

        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            while True:

                if not self.is_inside(nx, ny):
                    break

                cord: tuple[int, int] = (nx, ny)
                piece: Figure = self.get_piece(cord=cord)



                if piece:
                    if piece.color != enemy_color:
                        break

                    if isinstance(piece, expected_types):
                        return True
                    else:
                        break

                nx, ny = nx + dx, ny + dy
        return False


    def single_attack(self, enemy_color, expected_types, deltas, x, y):
        deltas = deltas

        for dx, dy in deltas:
            nx, ny = x + dx, y + dy

            if not self.is_inside(nx, ny):
                continue
            cord: tuple[int, int] = (nx, ny)
            piece: Figure = self.get_piece(cord=cord)
            if piece:
                return piece.color == enemy_color and isinstance(piece, expected_types)

        return False


    def find_king(self, color: PieceColor) -> tuple[int, int]:
        king = self.kings[color]
        return king.cord


    def __str__(self):
        text = ""
        for rows in self._board:
            for x in rows:
                text += f" {x} "
            text += "\n"
        return text
