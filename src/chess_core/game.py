from copy import deepcopy
from typing import Optional
from src.chess_core.chessboard import ChessBoard
from src.enums import MoveResult, PieceColor, MoveSpecial, GameStatus, ClickResult, Errors

from src.dataclass import Move, MoveRecord, CastlingRights, Stak, UpdateResult
from src.chess_core.shapes import Figure, King, Queen, Bishop, Knight, Rook, Pawn



class Game:
    def __init__(self):
        self.rows, self.cols = 8, 8
        self.tile_size = 70

        self.chessboard = ChessBoard()
        self.selected_piece: Figure = Figure()
        self.history: Stak = Stak()
        
        self.available_moves = []
        self.buffer: Move = None
        
        self.game_status = GameStatus.PLAYING
        self.has_move: PieceColor = PieceColor.WHITE        

        self.promotion_pos: tuple[int, int] = None
        self.first_select = False


    def update(self, board_x:int, board_y:int):
        data = {
            "game_status": GameStatus.PLAYING,
            "data": {},
            "errors": Errors.Nothing
        }

        if self.game_status == GameStatus.PLAYING:
            data["data"] = self._update_playing(board_x, board_y)
        
        elif self.game_status == GameStatus.PROMOTION_SELECT:
            data["data"] = self._update_promotion(board_x, board_y)


        elif self.game_status in (GameStatus.CHECKMATE, GameStatus.PAT):
            pass

        data["game_status"] = self.game_status

        return data


    def _update_playing(self, board_x:int, board_y:int):
        result = UpdateResult()
        
        result.type = self.analyze_select(pos=(board_x, board_y))
        piece = self.chessboard.get_piece(cord=(board_x, board_y))

        match result.type:
            case ClickResult.SELECT:
                self.selected_piece = piece
                self.first_select = True

                first_data = self._first_select(piece=piece)
                result.selected_piece = first_data["selected_piece"]
                result.moves = first_data["moves"]
                result.can_move = first_data["can_move"]


            case ClickResult.CHANGE_SELECTION:
                self.selected_piece = piece
                self.first_select = True

                first_data = self._first_select(piece=piece)
                result.selected_piece = first_data["selected_piece"]
                result.moves = first_data["moves"]
                result.can_move = first_data["can_move"]


            case ClickResult.SECOND_SELECT:
                self.first_select = False

            case ClickResult.MOVE:
                self.first_select = False

                second_data = self._second_select(board_x=board_x, board_y=board_y)
                result.move_from = second_data["move_from"]
                result.move_to = second_data["move_to"]
                result.move_result = second_data["move_result"]

            case ClickResult.NOTHING:
                pass

        if result.type == ClickResult.MOVE and result.move_result == MoveResult.OK:
            self._after_move()
        
        if (self.buffer and self.buffer.piece.color == self.has_move):
            current_piece = self.chessboard.get_piece(cord=self.buffer.from_pos)
            if (current_piece is self.buffer.piece):
                if (self.filter_move(move=self.buffer) == MoveResult.OK):
                    self._make_move(record=self.move_to_move_record(self.buffer))
                    self.buffer = None
                    self._after_move()

        return result

    def _update_promotion(self, board_x:int, board_y:int):
        piece: Figure = self.chessboard.get_piece(cord=self.promotion_pos)
        result = Figure

        x, y = self.promotion_pos
        
        dict_cord = {
            self.promotion_pos: Queen,
            (x, y - piece.direction * 1): Knight,
            (x, y - piece.direction * 2): Rook,
            (x, y - piece.direction * 3): Bishop
        }

        if (board_x, board_y) in dict_cord:
            fig: Figure = dict_cord[(board_x, board_y)]
            rec: MoveRecord = self.history.pop()
            self.chessboard.undo(rec)
            rec.promotion_pawn = fig(x=x, y=y, color=piece.color)
            self.chessboard.apply_move(rec)

            self._after_move()
            self.game_status = GameStatus.PLAYING
            result = fig

        return result

    def create_figures(self, texture_manager):
        logs = ""
        configs = {
            "black": {
                "color": PieceColor.BLACK,
                "fig_y": 7,
                "pawn_y": 6
            },
            "white": {
                "color": PieceColor.WHITE,
                "fig_y": 0,
                "pawn_y": 1
            }
        }
        for key, value in configs.items():
            logs += f"creating {key} figures \n"
            figures = get_figures_config(
                color=value["color"],
                fig_y=value["fig_y"],
                pawn_y=value["pawn_y"],
                texture_manager=texture_manager
            )

            for conf in figures.values():
                self.append_figures_on_board(
                    figures=get_figures_of_config(config=conf)
                )


    def append_figures_on_board(self, figures:list[Figure]):
        for fig in figures:
            x, y = fig.cord
            status = self.chessboard.add_figure(x=x, y=y, figure=fig)


    def _after_move(self):
        self.has_move = self.has_move.opposite()

        self.game_status = self.this_end(self.has_move)


    def analyze_select(self, *, pos: tuple[int, int]) -> ClickResult:
        piece = self.chessboard.get_piece(cord=pos)
        x, y = pos

        if not self.first_select:
            if piece:
                return ClickResult.SELECT
            return ClickResult.NOTHING


        if piece and piece.color == self.selected_piece.color:

            if self.selected_piece.cord == (x, y): # If it is second click on selected_piece then clear select
                return ClickResult.SECOND_SELECT
            return ClickResult.CHANGE_SELECTION

        if self.find_move_to(x, y):
            return ClickResult.MOVE

        return ClickResult.NOTHING


    def _first_select(self, *, piece: Figure):
        returned_data = {
            "selected_piece": piece,
            "moves": [],
            "can_move": True
        }

        moves = piece.get_moves(chessboard=self.chessboard)
        data = self.filter_moves(moves=moves)

        if data["moves_and_statuses"]: # If figure have at least one move
            right_moves = data["right_moves"]


            self.available_moves = right_moves
            returned_data["moves"] = right_moves

        if (piece.color != self.has_move):
            returned_data["can_move"] = False

        return returned_data


    def _second_select(self, *, board_x: int, board_y: int):
        data = {
            "move_from": (0, 0),
            "move_to": (0, 0),
            "move_result": MoveResult.NOTHING
        }

        move = self.find_move_to(to_x=board_x, to_y=board_y)

        record = self.move_to_move_record(move=move)

        data["move_from"] = record.from_pos
        data["move_to"] = record.to_pos

        last_line = 7 if record.piece.color == PieceColor.WHITE else 0

        if move:
            _, to_y = record.to_pos

            if isinstance(record.piece, Pawn) and to_y == last_line:
                self.promotion = True


            if record.piece.color == self.has_move:
                self._make_move(record=record)
                data["move_result"] = MoveResult.OK                
            else:
                if (not self.buffer): 
                    self.buffer = move
                    print("Buff work 1")
                else: self.buffer = None

        else:
            data["move_result"] =  MoveResult.ERROR

        return data


    def clear_available_moves(self):
        self.available_moves = []


    def _make_move(self, record: MoveRecord):
        self.chessboard.apply_move(record)

        self.history.push(record)
        self.available_moves.clear()


    def this_end(self, color) -> GameStatus:
        board = self.chessboard.get_board()
        king_pos = self.chessboard.find_king(color=color)
        kx, ky = king_pos
        king: Figure = board[ky][kx]
        king_moves = king.get_moves(chessboard=self.chessboard)
        right_moves = self.filter_moves(king_moves)["right_moves"]

        status = GameStatus.PLAYING

        # If king don't have moves
        if not right_moves:
            figures = self.chessboard.get_figures()

            for fig in figures:
                if fig.color == color:
                    moves = fig.get_moves(chessboard=self.chessboard)
                    right_moves = self.filter_moves(moves)["right_moves"]

                    # If any figure can move
                    if right_moves:
                        break

            # If all figures cannot make move
            else:
                king_is_check = self.chessboard.king_is_check(color=color)
                # Checkmate
                if king_is_check:
                    status = GameStatus.CHECKMATE
                else:
                    status = GameStatus.PAT

        return status


    def find_move_to(self, to_x, to_y) -> Optional[Move]:
        for move in self.available_moves:
            if move.to_pos == (to_x, to_y):
                return move

        return None


    def filter_moves(self, moves: list[Move]) -> dict:
        dic: dict = {
            "right_moves": [],
            "moves_and_statuses": {}
        }

        if moves:
            for move in moves:
                status = self.filter_move(move)

                dic["moves_and_statuses"][move] = status
                if status == MoveResult.OK:
                    dic["right_moves"].append(move)

            return dic

        return dic


    def filter_move(self, move: Move):
        mr = self.move_to_move_record(move=move)

        self.chessboard.apply_move(mr)
        king_is_check: bool = self.chessboard.king_is_check(move.piece.color)
        self.chessboard.undo(mr)


        if move.special in (MoveSpecial.CASTLE_KINGSIDE, MoveSpecial.CASTLE_QUEENSIDE):
            if not self.can_king_castle(move_record=mr):
                return MoveResult.INVALID_MOVE


        if king_is_check:
            return MoveResult.CHECK
        return MoveResult.OK


    def can_king_castle(self, *, move_record: MoveRecord):
        from_x, _ = move_record.from_pos
        to_x, _ = move_record.to_pos
        y = _
        direction = move_record.piece.direction
        for x in range(from_x, to_x + direction, direction):
            if self.chessboard.is_square_attacked(
                        x=x,
                        y=y,
                        enemy=move_record.piece.color.opposite()
                    ):
                return False
        return True


    def move_to_move_record(self, move: Move):
        captured_piece: Optional[Figure] = None
        captured_pos: Optional[tuple[int, int]] = None

        rook: Optional[Figure] = None
        rook_from: Optional[tuple[int, int]] = None
        rook_to: Optional[tuple[int, int]] = None

        prev_castling_rights: CastlingRights = deepcopy(self.chessboard.castling_rights)
        prev_en_passant: Optional[tuple[int, int]] = self.chessboard.en_passant_target

        board = self.chessboard.get_board()
        new_x, new_y = move.to_pos

        rank = move.piece.direction

        match move.special:
            case MoveSpecial.CAPTURE:
                captured_piece = board[new_y][new_x]
                captured_pos = (new_x, new_y)

            case MoveSpecial.CASTLE_KINGSIDE:

                rook = board[new_y][new_x - 1]
                rook_from = (new_x - 1, new_y)
                rook_to = (new_x + 1, new_y)

            case MoveSpecial.CASTLE_QUEENSIDE:

                rook = board[new_y][new_x + 2]
                rook_from = (new_x + 2, new_y)
                rook_to = (new_x - 1, new_y)

            case MoveSpecial.EN_PASSANT:
                prev_en_pas_x, prev_en_pas_y = prev_en_passant
                prev_en_pas_y -= rank
                captured_piece = self.chessboard.get_piece(cord=(prev_en_pas_x, prev_en_pas_y))
                captured_pos = (prev_en_pas_x, prev_en_pas_y)


        mr = MoveRecord(
            piece=move.piece,
            from_pos=move.from_pos,
            to_pos=move.to_pos,

            captured_piece = captured_piece,
            captured_pos = captured_pos,

            rook = rook,
            rook_from = rook_from,
            rook_to = rook_to,

            prev_castling_rights= prev_castling_rights,
            prev_en_passant= prev_en_passant
        )
        return mr


    # interfaces:
    def get_chessboard(self):
        return self.chessboard


    def get_game_info(self):
        return {
            "who move": self.has_move,
            "status": self.game_status
        }


    def clear_promotion_figure(self):
        self.promotion_figure = None


    def get_current_king_status(self):
        """
        Returns: True if king check and False if king not check
        """
        return self.chessboard.king_is_check(self.has_move)



def make_promotion(fig: Figure, record):
    x, y = record.to_pos
    figure = fig(x=x, y=y, color=record.piece.color)
    record.promotion_pawn = figure
    return record


def get_figures_of_config(*, config) -> list[Figure]:
    figures: list[Figure] = []

    for i in range(config["count"]):
        fig_type: Figure = config["type"]
        x, y = config["cords"][i]
        color: PieceColor = config["color"]
        texture = config["texture"]
        figures.append(fig_type(x=x, y=y, color=color, texture=texture))
    return figures


def get_figures_config(*, color, fig_y, pawn_y, texture_manager):
    return {
        "king": {
            "type": King,
            "count": 1,
            "cords": [(3, fig_y)],
            "color": color,
            "texture": texture_manager.get_texture(f"{color}_king")
        },
        "queen": {
            "type": Queen,
            "count": 1,
            "cords": [(4, fig_y)],
            "color": color,
            "texture": texture_manager.get_texture(f"{color}_queen")
        },
        "bishops": {
            "type": Bishop,
            "count": 2,
            "cords": [(5, fig_y), (2, fig_y)],
            "color": color,
            "texture": texture_manager.get_texture(f"{color}_bishop")
        },
        "knights": {
            "type": Knight,
            "count": 2,
            "cords": [(6, fig_y), (1, fig_y)],
            "color": color,
            "texture": texture_manager.get_texture(f"{color}_knight")
        },
        "rooks": {
            "type": Rook,
            "count": 2,
            "cords": [(7, fig_y), (0, fig_y)],
            "color": color,
            "texture": texture_manager.get_texture(f"{color}_rook")
        },
        "pawns": {
            "type": Pawn,
            "count": 8,
            "cords": [(x, pawn_y) for x in range(8)],
            "color": color,
            "texture": texture_manager.get_texture(f"{color}_pawn")
        }
    }


def select_promotion_figure(cord, direction, board_x, board_y):
    x, y = cord

    dict_cord = {
        cord: Queen,
        (x, y - direction * 1): Knight,
        (x, y - direction * 2): Rook,
        (x, y - direction * 3): Bishop
    }
    if not (board_x, board_y) in dict_cord.keys():
        return 0
    fig = dict_cord[(board_x, board_y)]
    return fig
