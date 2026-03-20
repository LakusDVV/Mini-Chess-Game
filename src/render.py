import os
import raylibpy as rl
from typing import TYPE_CHECKING
from src.paths import IMAGES_DIR
from src.enums import PieceColor



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
        self._load("black_king",    "black_king.png")
        self._load("black_queen",   "black_queen.png")
        self._load("black_rook",    "black_rook.png")
        self._load("black_bishop",  "black_bishop.png")
        self._load("black_knight",  "black_knight.png")
        self._load("black_pawn",    "black_pawn.png")
        self._load("white_king",    "white_king.png")
        self._load("white_queen",   "white_queen.png")
        self._load("white_rook",    "white_rook.png")
        self._load("white_bishop",  "white_bishop.png")
        self._load("white_knight",  "white_knight.png")
        self._load("white_pawn",    "white_pawn.png")
        self._load("highlighting",  "highlighting_texture.png")


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
        self.radius = self.tile_size // 5.5
        # width = self.cols * self.tile_size
        # height = self.rows * self.tile_size



        self._chessboard: ChessBoard = chessboard
        self.texture_manager = texture_manager
        self.light_color = rl.Color(r=240, g=217, b=181, a=255)
        self.dark_color = rl.Color(r=181, g=136, b=99, a=255)


        self.highlighting_data = {
            "has_data": False,
            "captures": [],
            "moves": [],
            "color":  rl.Color(r=129, g=151, b=105, a=255)
        }

        self.last_move_data = {
            "has_data": False,
            "data": [(1, 1), (1, 1)],
            "color": rl.Color(r=154, g=200, b=0, a=90)
        }

        self.check_data: dict = {
            "has_data": False,
            "data": (),
            "color":  rl.Color(r=230, g=41, b=55, a=120)
        }

        self.promotion_pawn_data = {
            "has_data": False,
            "data": {
                "color": PieceColor.WHITE,
                "direction": 0, # -1 or 1
                "cord": (0, 0) # (x, y)
            }
        }

        self.highlighting_the_selected_cell_data = {
            "has_data": False,
            "data": (1, 1),
            "color": rl.Color(r=113, g=115, b=70, a=160)
        }

        self.highlighting_of_the_selected_cell_data ={
            "has_data": False,
            "data": (1, 1),
            "color": rl.Color(r=22, g=88, b=30, a=130)
        }


    def get_tile_color(self, x: int, y: int) -> rl.Color:
        """
        Returns the color tile for the tile

        Args:
            x (int): cord x tile
            y (int): cord y tile

        Returns:
            rl.Color: the color tile
        """
        return self.light_color if (x + y) % 2 == 0 else self.dark_color


    def draw(self):
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)

        self.draw_tiles()
        self.draw_highlighting_selected_cell()
        self.draw_highlighting_of_the_selected_cell()
        self.draw_last_move()
        self.draw_figures()
        self.draw_highlighting()
        self.draw_check_king()
        self.draw_select_promotion_pawn()

        rl.end_drawing()


    def draw_tiles(self) -> None:
        """
        Draw tiles
        """

        for y in range(self.cols):
            for x in range(self.rows):
                color = self.get_tile_color(x, y)
                rl.draw_rectangle(
                    pos_x= x * self.tile_size,
                    pos_y= y * self.tile_size,
                    width= self.tile_size,
                    height= self.tile_size,
                    color= color
                )


    def draw_figures(self) -> None:

        figures = self._chessboard.get_figures()

        for fig in figures:
            fig.draw()



    # highlighting moves block <
    def draw_highlighting(self) -> None:
        highlighting_texture = self.texture_manager.get_texture("highlighting")
        cel_x, cel_y = self.highlighting_of_the_selected_cell_data["data"]
        tr = self.highlighting_of_the_selected_cell_data["has_data"]

        if self.highlighting_data["has_data"]:
            for nx, ny in self.highlighting_data["captures"]:
                tx = nx * self.tile_size
                ty = ny * self.tile_size
                if tr and (nx, ny) == (cel_x, cel_y):
                    continue


                rl.draw_texture(
                    texture=highlighting_texture,
                    pos_x=tx,
                    pos_y=ty,
                    tint=rl.WHITE
                )

            for nx, ny in self.highlighting_data["moves"]:
                cx = nx * self.tile_size + self.tile_size // 2
                cy = ny * self.tile_size + self.tile_size // 2
                if tr and (nx, ny) == (cel_x, cel_y):
                    continue

                rl.draw_circle(
                    center_x=cx,
                    center_y=cy,
                    radius=self.radius,
                    color=self.highlighting_data["color"]
                )


    def change_highlighting_data(self, captures: list, moves: list):
        if captures or moves:
            self.highlighting_data["has_data"] = True
            self.highlighting_data["captures"] = captures
            self.highlighting_data["moves"] = moves


    def clear_highlighting_data(self):
        self.highlighting_data["has_data"] = False
    # highlighting moves block >



    # highlighting selected cell block <
    def draw_highlighting_selected_cell(self) -> None:
        if self.highlighting_the_selected_cell_data["has_data"]:
            x, y = self.highlighting_the_selected_cell_data["data"]
            rl.draw_rectangle(
                pos_x=x * self.tile_size,
                pos_y=y * self.tile_size,
                width=self.tile_size,
                height=self.tile_size,
                color=self.highlighting_the_selected_cell_data["color"]
            )


    def change_highlighting_selected_cell_data(self, cord:tuple[int, int]):
        self.highlighting_the_selected_cell_data["data"] = cord
        self.highlighting_the_selected_cell_data["has_data"] = True


    def clear_highlighting_selected_cell_data(self):
        self.highlighting_the_selected_cell_data["has_data"] = False

    # highlighting selected cell block >



    # highlighting selected cell block <
    def draw_highlighting_of_the_selected_cell(self) -> None:
        if self.highlighting_of_the_selected_cell_data["has_data"]:
            x, y = self.highlighting_of_the_selected_cell_data["data"]
            rl.draw_rectangle(
                pos_x=x * self.tile_size,
                pos_y=y * self.tile_size,
                width=self.tile_size,
                height=self.tile_size,
                color=self.highlighting_of_the_selected_cell_data["color"]
            )


    def change_highlighting_of_the_selected_cell_data(self, cord: tuple[int, int]):
        self.highlighting_of_the_selected_cell_data["data"] = cord
        self.highlighting_of_the_selected_cell_data["has_data"] = True


    def clear_highlighting_of_the_selected_cell_data(self):
        self.highlighting_of_the_selected_cell_data["has_data"] = False
    # highlighting selected cell block >



    # check king block <
    def draw_check_king(self) -> None:
        if self.check_data["has_data"]:
            x, y = self.check_data["data"]
            rl.draw_rectangle(
                pos_x=x * self.tile_size,
                pos_y=y * self.tile_size,
                width=self.tile_size,
                height=self.tile_size,
                color=self.check_data["color"]
            )


    def change_check_data(self, new_pos: tuple[int, int]):
        self.check_data["data"] = new_pos
        self.check_data["has_data"] = True


    def clear_check_data(self):
        self.check_data["data"] = ()
        self.check_data["has_data"] = False
    # check king block >



    # promotion pawn block <
    def draw_select_promotion_pawn(self) -> None:
        if self.promotion_pawn_data["has_data"]:
            data = self.promotion_pawn_data["data"]

            if data["color"] == PieceColor.WHITE:
                queen_t = self.texture_manager.get_texture("white_queen")
                knight_t = self.texture_manager.get_texture("white_knight")
                rook_t = self.texture_manager.get_texture("white_rook")
                bishop_t = self.texture_manager.get_texture("white_bishop")
            else:
                queen_t = self.texture_manager.get_texture("black_queen")
                knight_t = self.texture_manager.get_texture("black_knight")
                rook_t = self.texture_manager.get_texture("black_rook")
                bishop_t = self.texture_manager.get_texture("black_bishop")

            x, y = data["cord"]
            direct = data["direction"]


            rl.draw_texture(
                texture=queen_t,
                pos_x=x * self.tile_size,
                pos_y=y * self.tile_size,
                tint=rl.WHITE
            )

            rl.draw_texture(
                texture=knight_t,
                pos_x=x * self.tile_size,
                pos_y=(y - direct * 1) * self.tile_size,
                tint=rl.WHITE
            )

            rl.draw_texture(
                texture=rook_t,
                pos_x=x * self.tile_size,
                pos_y=(y - direct * 2) * self.tile_size,
                tint=rl.WHITE
            )
            rl.draw_texture(
                texture=bishop_t,
                pos_x=x * self.tile_size,
                pos_y=(y - direct * 3) * self.tile_size,
                tint=rl.WHITE
            )


    def change_promotion_pawn_data(self, color: PieceColor, direction: int, cord: tuple[int, int]):
        self.promotion_pawn_data["has_data"] = True
        self.promotion_pawn_data["data"]["color"] = color
        self.promotion_pawn_data["data"]["direction"] = direction
        self.promotion_pawn_data["data"]["cord"] = cord


    def clear_promotion_pawn_data(self):
        self.promotion_pawn_data["has_data"] = False
    # promotion pawn block >



    # last move block <
    def draw_last_move(self) -> None:
        if self.last_move_data["has_data"]:
            for x, y in self.last_move_data["data"]:
                rl.draw_rectangle(
                    pos_x=x * self.tile_size,
                    pos_y=y * self.tile_size,
                    width=self.tile_size,
                    height=self.tile_size,
                    color=self.last_move_data["color"]
                )


    def change_last_move_data(self, from_pos: tuple[int, int], to_pos: tuple[int, int]):
        self.last_move_data["data"] = [from_pos, to_pos]
        self.last_move_data["has_data"] = True


    def clear_last_move_data(self):
        self.last_move_data["has_data"] = False
    # last move block >
