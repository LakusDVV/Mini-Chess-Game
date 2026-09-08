import os
import raylibpy as rl
from typing import TYPE_CHECKING
from src.paths import IMAGES_DIR
from src.enums import PieceColor
from src.render_dataclasses import HighlightingData, PositionData


if TYPE_CHECKING:
    from src.chess_core.chessboard import ChessBoard


class RenderComponent:
    def __init__(self, texture):
        self.texture = texture


    def draw(self, *, x, y, tile_size):
        rl.draw_texture(
            texture=self.texture,
            pos_x=x * tile_size,
            pos_y=y * tile_size,
            tint= rl.WHITE
        )


class TextureManager:
    def __init__(self):
        self._textures = {}


    def load_textures(self):
        self._load("black_king",                "black_king.png")
        self._load("black_queen",               "black_queen.png")
        self._load("black_rook",                "black_rook.png")
        self._load("black_bishop",              "black_bishop.png")
        self._load("black_knight",              "black_knight.png")
        self._load("black_pawn",                "black_pawn.png")
        self._load("white_king",                "white_king.png")
        self._load("white_queen",               "white_queen.png")
        self._load("white_rook",                "white_rook.png")
        self._load("white_bishop",              "white_bishop.png")
        self._load("white_knight",              "white_knight.png")
        self._load("white_pawn",                "white_pawn.png")
        self._load("highlighting",              "highlighting_texture.png")
        self._load("highlighting_next_move",    "highlighting_next_move_texture.png")


    def _load(self, key: str, filename: str):
        path = os.path.join(IMAGES_DIR, filename)

        if not rl.is_window_ready():
            raise RuntimeError("Window not initialized before loading texture")

        texture = rl.load_texture(path)
        assert texture.id != 0, f"Failed to load texture: {path}"
        self._textures[key] = texture


    def get_texture(self, name):
        return self._textures[name]


class Render:
    """
    Class for draw

    """
    def __init__(self, *, chessboard, texture_manager: TextureManager):
        self.rows = 8
        self.cols = 8
        self.tile_size = 70
        self.piece_radius = self.tile_size // 5.5
        # width = self.cols * self.tile_size
        # height = self.rows * self.tile_size



        self._chessboard: ChessBoard = chessboard
        self.texture_manager = texture_manager
        
        self._colors = {
            "light":        rl.Color(r=240, g=217, b=181, a=255),
            "dark":         rl.Color(r=181, g=136, b=99, a=255),
            "moves":        rl.Color(r=129, g=151, b=105, a=255),
            "next_moves":   rl.Color(r=147, g=108, b=182, a=140),
            "selected":     rl.Color(r=113, g=115, b=70, a=160),
            "check":        rl.Color(r=230, g=41, b=55, a=120),
            "last_move":    rl.Color(r=154, g=200, b=0, a=90)
        }
        self._highlights = {
            "moves":        HighlightingData(captures=[], moves=[], color=self._colors["moves"], texture_name="highlighting"),
            "next_moves":   HighlightingData(captures=[], moves=[], color=self._colors["next_moves"], texture_name="highlighting_next_move"),
            "selected":     PositionData(position=[], color=self._colors["selected"]),
            "howered":      PositionData(position=[], color=self._colors["selected"]),
            "check":        PositionData(position=[], color=self._colors["check"]),
            "last_move":    PositionData(position=[], color=self._colors["last_move"])        
        }
        

        self.promotion_pawn_data = {
            "has_data": False,
            "data": {
                "color": PieceColor.WHITE,
                "direction": 0, # -1 or 1
                "cord": (0, 0) # (x, y)
            }
        }
    

    def draw(self):
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)

        # Draw the first layer, the board 
        self.draw_board()        

        # Draw the highlights
        for name in ["selected", "howered", "last_move", "check"]:
            self.draw_highlight_rectangle(self._highlights[name])

        # Draw the thirs layer, the figures
        self.draw_figures()

        # Draw moved and captures
        self.draw_move_indecators()

        # Promotion
        self.draw_promotion_menu()
                
        rl.end_drawing()


    def draw_board(self) -> None:
        """
        Drawing board
        """

        for y in range(self.cols):
            for x in range(self.rows):
                self.draw_rectangle(x, y)
                
    def draw_rectangle(self, x, y):
        color = self.get_tile_color(x, y)
        rl.draw_rectangle(
            pos_x= x * self.tile_size,
            pos_y= y * self.tile_size,
            width= self.tile_size,
            height= self.tile_size,
            color= color
        )

    def get_tile_color(self, x: int, y: int) -> rl.Color:
        """
        Returns the color tile for the tile
        """
        return self._colors["light"] if (x + y) % 2 == 0 else self._colors["dark"]


    def draw_figures(self) -> None:
        figures = self._chessboard.get_figures()

        for fig in figures:
            fig.draw()


    def draw_move_indecators(self):
        target = "moves"
        if self._highlights[target].moves == [] and self._highlights[target].captures == []:
            target = "next_moves"
        
        if self._highlights[target].moves or self._highlights[target].captures:
            highlight: HighlightingData = self._highlights[target]
            highlight_hower: PositionData = self._highlights["howered"]

            for x, y in highlight.moves:
                if not highlight_hower.position == [(x, y)]:
                    self.draw_circle_at(x=x, y=y, color=highlight.color)
            
            for x, y in highlight.captures:
                if not highlight_hower.position == [(x, y)]:
                    self.draw_texture_at(x=x, y=y, texture_name=highlight.texture_name)

    def draw_promotion_menu(self):
        if self.promotion_pawn_data["has_data"]:
            data = self.promotion_pawn_data["data"]
            pawn_x, pawn_y = data["cord"]
            figure_order = ["queen", "knight", "rook", "bishop"]

            conf = {
                pawn_y - data["direction"]  * (i): figure_order[i]
                for i in range(4)
            }

            
            for ty, fig in conf.items():
                self.draw_rectangle(pawn_x, ty)
                self.draw_texture_at(pawn_x, ty, f"{data["color"]}_{fig}")



    def draw_circle_at(self, x:int, y:int, color: rl.Color):
        cx = x * self.tile_size + self.tile_size // 2
        cy = y * self.tile_size + self.tile_size // 2
        rl.draw_circle(
            center_x=cx,
            center_y=cy,
            radius=self.piece_radius,
            color=color
        )
    

    def draw_texture_at(self, x:int, y:int, texture_name:str) -> None:
        texture = self.texture_manager.get_texture(texture_name)
        rl.draw_texture(
            pos_x= x * self.tile_size,
            pos_y= y * self.tile_size,
            texture=texture,
            tint=rl.WHITE
        )


    def draw_highlight_rectangle(self, highlight: PositionData) -> None:
        
        if not highlight.position:
            return

        for x, y in highlight.position:            
            rl.draw_rectangle(
                pos_x=x * self.tile_size,
                pos_y=y * self.tile_size,
                width=self.tile_size,
                height=self.tile_size,
                color=highlight.color
            )


    def set_data_highlight(self, *, position, name_highlight) -> None:
        self._highlights[name_highlight].position = position

        
    def set_data_moves(self, *, captures, moves, moves_type):
        self._highlights[moves_type].moves = moves
        self._highlights[moves_type].captures = captures


    def clear_highlight_data(self, *, name_highlight) -> None:
        self._highlights[name_highlight].clear()

    def set_promotion_data(self, cord: tuple[int, int], color: PieceColor, direction: int):
        self.promotion_pawn_data["has_data"] = True
        self.promotion_pawn_data["data"] = {
                "color": color,
                "direction": direction, # -1 or 1
                "cord": cord # (x, y)
            }

    def clear_promotion_data(self):
        self.promotion_pawn_data["has_data"] = False

    