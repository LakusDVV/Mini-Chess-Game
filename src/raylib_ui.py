import raylibpy as rl
from src.render import Render, TextureManager
from src.chess_core.game import Game
from src.enums import GameStatus


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
        self.cheker_on = False
        self.cheker = 0

        self.render = Render(chessboard=self.chess_game.get_chessboard(), texture_manager=self.texture_manager)

        self.chess_game.create_figures(texture_manager=self.texture_manager)


    def run(self):
        while not rl.window_should_close():
            self.render.draw()
            self.update()

        rl.close_window()


    def update(self):
        mouse_x = rl.get_mouse_x()
        mouse_y = rl.get_mouse_y()

        board_x = mouse_x // self.tile_size
        board_y = mouse_y // self.tile_size

        if self.cheker_on:
            self.cheking_cell(board_x, board_y)


        mouse_click: bool = rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON)

        if mouse_click:
            self.clear_render_data_first_click()
            self.clear_render_data_second_click()

            game_data = self.chess_game.update(board_x=board_x, board_y=board_y)
            
            if game_data["game_status"] == GameStatus.IN_PROGRESS:
                if game_data["select_number"] == 1:
                    self.update_highlighting_first_data(game_data["first_data"])
                    self.clear_render_data_second_click()
                elif game_data["select_number"] == 2:
                    self.update_highlighting_second_data(game_data["second_data"])
                    self.clear_render_data_first_click()

            print(self.chess_game.get_game_info())

        


    def update_highlighting_first_data(self, first_data):
        if first_data:
            captures = []
            moves = []
            for move in first_data["moves"]:
                if move.special is None:
                    moves.append(move.to_pos)
                else:
                    captures.append(move.to_pos)
            
            self.render.set_data_moves(captures=captures, moves=moves)
            self.render.set_data_highlight(position=first_data["selected_piece"].cord, name_highlight="selected")
            self.cheker = remember_available_moves(moves)
            self.cheker_on = True
        else:
            self.render.clear_highlight_data(name_highlight="howerd")
            self.render.clear_highlight_data(name_highlight="selected")
            self.cheker_on = False
 

    def cheking_cell(self, x, y):
        draw_on = self.cheker(x, y)
        if draw_on:
            self.render.set_data_highlight(position=[(x, y)], name_highlight="howered")
        else:
            self.render.clear_highlight_data(name_highlight="howered")


    def clear_render_data_first_click(self):
        self.render.clear_highlight_data(name_highlight="moves")
        self.render.clear_highlight_data(name_highlight="howerd")
        self.render.clear_highlight_data(name_highlight="selected")
        self.cheker_on = False


    def update_highlighting_second_data(self, second_data):
        self.render.set_data_highlight(position=[second_data["move_from"], second_data["move_to"]], name_highlight="last_move")


    def clear_render_data_second_click(self):
        self.render.clear_highlight_data(name_highlight="last_move")


def remember_available_moves(data):
    def is_in_available_move(mouse_x, mouse_y):
        if (mouse_x, mouse_y) in data:
            return True
        return False
    
    return is_in_available_move
