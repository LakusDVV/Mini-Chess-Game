from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
from src.enums import PieceColor, MoveSpecial

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
class History:
    def __init__(self):
        self._history: list[MoveRecord] = []

    def push(self, item) -> None:
        self._history.append(item)


    def top(self) -> MoveRecord:
        return self._history[-1]


    def pop(self) -> MoveRecord:
        return self._history.pop()


    def is_empty(self):
        return len(self._history) == 0
