from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
from src.enums import PieceColor, MoveSpecial
import raylibpy as rl


@dataclass
class HighlightingData:
    captures: list[tuple[int, int]]
    moves: list[tuple[int, int]] 

    color: rl.Color = None
    texture_name: str = None

    def clear(self):
        self.captures = []
        self.moves = []

    
@dataclass
class PositionData:
    position: list[tuple[int, int]]

    color: rl.Color = None

    def clear(self):
        self.position = []


@dataclass
class PromotionMenu:
    piece_color: PieceColor
    direction: int

    
