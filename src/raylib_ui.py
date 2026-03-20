import raylibpy as rl
from src.render import Render, TextureManager
from src.chess_core.game import Game


class Game_UI:
    def __init__(self):
        self.chess_game = Game()




        self.rows = 8
        self.cols = 8
        self.tile_size = 70
        width = self.cols * self.tile_size
        height = self.rows * self.tile_size

        rl.init_window(width, height, "Chess")
        rl.set_target_fps(60)

        self.texture_manager = TextureManager()
        self.texture_manager.load_textures()

        self.render = Render(chessboard=self.chess_game.get_chessboard(), texture_manager=self.texture_manager)


        self.chess_game.create_figures(texture_manager= self.texture_manager)




    def run(self):
        while not rl.window_should_close():
            self.render.draw()
            self.update()

        rl.close_window()


    def update(self):
        mouse_x = rl.get_mouse_x()
        mouse_y = rl.get_mouse_y()


        mouse_click: bool = rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON)

        if mouse_click:
            board_x = mouse_x // self.tile_size
            board_y = mouse_y // self.tile_size

            game_data = self.chess_game.update(board_x=board_x, board_y=board_y)

            print(game_data)
