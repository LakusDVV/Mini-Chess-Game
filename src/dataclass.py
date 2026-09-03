from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from src.enums import PieceColor, MoveSpecial, ClickResult, MoveResult

if TYPE_CHECKING:
    from src.chess_core.shapes import Figure


@dataclass(frozen=True)
class Move:
    piece: "Figure"
    from_pos: tuple[int, int]
    to_pos: tuple[int, int]
    special: Optional[MoveSpecial] = None  # "castle_kingside", "castle_queenside", "en_passant", "promotion_pawn", "capture"


@dataclass
class CastlingRights:
    white_king_side: bool = True
    white_queen_side: bool = True
    black_king_side: bool = True
    black_queen_side: bool = True

    def can_castle_kingside(self, color: PieceColor):
        return (
            self.white_king_side
            if color == PieceColor.WHITE
            else self.black_king_side
        )

    def can_castle_queenside(self, color: PieceColor):
        return (
            self.white_queen_side
            if color == PieceColor.WHITE
            else self.black_queen_side
        )



@dataclass
class MoveRecord:
    piece: "Figure"
    from_pos: tuple[int, int]
    to_pos: tuple[int, int]

    captured_piece: Optional["Figure"] = None
    captured_pos: Optional[tuple[int, int]] = None

    rook: Optional["Figure"] = None
    rook_from: Optional[tuple[int, int]] = None
    rook_to: Optional[tuple[int, int]] = None

    prev_castling_rights: CastlingRights = None
    prev_en_passant: Optional[tuple[int, int]] = None

    promotion_pawn: Optional["Figure"] = None


@dataclass
class UpdateResult:
    type: ClickResult = ClickResult.NOTHING
    selected_piece: Optional[Figure] = None
    moves: list = field(default_factory=list)
    can_move: bool = True
    move_from: tuple = (0, 0)
    move_to: tuple = (0, 0)
    move_result: MoveResult = MoveResult.NOTHING


@dataclass
class Stak:
    _list: list = field(default_factory=list)

    def push(self, item) -> None:
        self._list.append(item)


    def top(self):
        return self._list[-1]


    def pop(self):
        return self._list.pop()


    def is_empty(self):
        return len(self._list) == 0
