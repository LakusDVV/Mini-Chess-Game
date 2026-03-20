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
            

            game_data = self.chess_game.update(board_x=board_x, board_y=board_y)
            
            if game_data["game_status"] == GameStatus.IN_PROGRESS:
                if game_data["select_number"] == 1:
                    self.update_highlighting_first_data(game_data["first_data"])
                    self.clear_render_data_second_click()
                elif game_data["select_number"] == 2:
                    self.update_highlighting_second_data(game_data["second_data"])
                    self.clear_render_data_first_click()

        


    def update_highlighting_first_data(self, first_data):
        if first_data:
            captures = []
            moves = []
            for move in first_data["moves"]:
                if move.special is None:
                    moves.append(move.to_pos)
                else:
                    captures.append(move.to_pos)
            
            self.render.change_highlighting_data(captures=captures, moves=moves)
            self.render.change_highlighting_selected_cell_data(first_data["selected_piece"].cord)
            self.cheker = remember_available_moves(moves)
            self.cheker_on = True
 

    def cheking_cell(self, x, y):
        draw_on = self.cheker(x, y)
        if draw_on:
            self.render.change_highlighting_of_the_selected_cell_data((x, y))
        else:
            self.render.clear_highlighting_of_the_selected_cell_data()


    def clear_render_data_first_click(self):
        self.render.clear_highlighting_data()
        self.render.clear_highlighting_of_the_selected_cell_data()
        self.render.clear_highlighting_selected_cell_data()
        self.cheker_on = False


    def update_highlighting_second_data(self, second_data):        
        if second_data:
            self.render.change_last_move_data(from_pos=second_data["move_from"], to_pos=second_data["move_to"])


    def clear_render_data_second_click(self):
        self.render.clear_last_move_data()


def remember_available_moves(data):
    def is_in_available_move(mouse_x, mouse_y):
        if (mouse_x, mouse_y) in data:
            return True
        return False
    
    return is_in_available_move
