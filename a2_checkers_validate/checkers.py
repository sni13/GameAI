import sys

COLOR_RED = "r"
COLOR_RED_KING = "R"
COLOR_BLUE = "b"
COLOR_BLUE_KING = "B"
EMPTY = "."

max_cache = {}
min_cache = {}

def get_possible_moves(board, color):
    move_shifts = []
    move_jumps = []
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j].lower() == color:
                move_jumps += get_piece_jumps(board, (i, j))
                if not move_jumps:
                    move_shifts += get_piece_shifts(board, (i, j))

    if move_jumps:
        return move_jumps
    else:
        return move_shifts


def get_piece_direct_jumps(board, piece_coord):
    piece_x, piece_y = piece_coord
    piece = board[piece_x][piece_y]
    direct_jump_dests = []

    up = [
        ((piece_x - 1, piece_y - 1), (piece_x - 2, piece_y - 2)),
        ((piece_x - 1, piece_y + 1), (piece_x - 2, piece_y + 2))
    ]
    down = [
        ((piece_x + 1, piece_y - 1), (piece_x + 2, piece_y - 2)),
        ((piece_x + 1, piece_y + 1), (piece_x + 2, piece_y + 2))
    ]

    if piece == COLOR_RED or piece.isupper():
        for neighbor, dest in up:
            if valid_coord(neighbor) and valid_coord(dest) and \
                    board[neighbor[0]][neighbor[1]].lower() == get_other_color(piece.lower()) and \
                    board[dest[0]][dest[1]] == EMPTY:
                direct_jump_dests.append(dest)

    if piece == COLOR_BLUE or piece.isupper():
        for neighbor, dest in down:
            if valid_coord(neighbor) and valid_coord(dest) and \
                    board[neighbor[0]][neighbor[1]].lower() == get_other_color(piece.lower()) and \
                    board[dest[0]][dest[1]] == EMPTY:
                direct_jump_dests.append(dest)

    return direct_jump_dests
    
def get_board_after_jump(board, piece_coord, dest):
    res = ()
    piece = board[piece_coord[0]][piece_coord[1]]
    neighbor = (int((piece_coord[0] + dest[0]) / 2), int((piece_coord[1] + dest[1]) / 2))

    for i in range(len(board)):
        row = ()

        for j in range(len(board[i])):
            if (i, j) == piece_coord or (i, j) == neighbor:
                row += (EMPTY,)
            elif (i, j) == dest:
                if (piece == COLOR_RED and i == 0) or (piece == COLOR_BLUE and i == 7):
                    row += (piece.upper(),)
                else:
                    row += (piece,)
            else:
                row += (board[i][j],)
        res += (row,)
    return res

def get_piece_jumps(board, piece_coord): # -> move - [(start_x, start_y), ...., (dest_x, dest_y)]
    moves = []
    direct_jump_dests = get_piece_direct_jumps(board, piece_coord) # [(dest_x, dest_y), .....]

    if not direct_jump_dests:
        return []
    
    for direct_jump_dest in direct_jump_dests:

        result_board = get_board_after_jump(board, piece_coord, direct_jump_dest)
        future_jumps = get_piece_jumps(result_board, direct_jump_dest)

        if future_jumps:
            for future_jump in future_jumps:
                moves.append([piece_coord] + future_jump)
        else:
            moves.append([piece_coord, direct_jump_dest])

    return moves    

def get_piece_shifts(board, piece_coord):
    piece_x, piece_y = piece_coord
    piece = board[piece_x][piece_y]
    moves = []

    up = [(piece_x - 1, piece_y - 1), (piece_x - 1, piece_y + 1)]
    down = [(piece_x + 1, piece_y - 1), (piece_x + 1, piece_y + 1)]
    
    if piece == COLOR_RED or piece.isupper():
        for coord in up:
            if valid_coord(coord) and board[coord[0]][coord[1]] == EMPTY:
                moves.append([piece_coord, coord])
    
    if piece == COLOR_BLUE or piece.isupper():
        for coord in down:
            if valid_coord(coord) and board[coord[0]][coord[1]] == EMPTY:
                moves.append([piece_coord, coord])

    return moves

def get_result_board(board, move):
    res = ()

    start_coord = move[0]
    dest_coord = move[-1]
    intermediate_coords = move[:-1]
    neighbor_coords = []

    for i in range(len(move) - 1):
        prev_coord = move[i]
        after_coord = move[i + 1]

        # Direct shift
        if abs(after_coord[0] - prev_coord[0]) == 1:
            break

        neighbor_coords.append((int((prev_coord[0] + after_coord[0]) / 2), int((prev_coord[1] + after_coord[1]) / 2)))

    piece = board[start_coord[0]][start_coord[1]]
    if piece == COLOR_RED:
        for coord in move:
            if coord[0] == 0:
                piece = piece.upper()
    if piece == COLOR_BLUE:
        for coord in move:
            if coord[0] == 7:
                piece = piece.upper()

    for i in range(len(board)):
        row = ()

        for j in range(len(board[i])):
            if (i, j) == dest_coord:
                row += (piece,)
            elif (i, j) in intermediate_coords or (i, j) in neighbor_coords:
                row += (EMPTY,)
            else:
                row += (board[i][j],)
        res += (row,)
    return res


def get_other_color(color):
    return "b" if color == "r" else "r"

def valid_coord(coord):
    return 0 <= coord[0] <= 7 and 0 <= coord[1] <= 7

def get_board_str(board):
    res = ''
    for row in board:
        for piece in row:
            res += piece
        res += '\n'
    return res.strip()


def get_color_score(board, color):
    count = 0
    for row in board:
        for cell in row:
            if cell == color.lower():
                count += 1
            elif cell == color.upper():
                count += 2
    return count


def utility(board, color):
    score_color = get_color_score(board, color)
    oppo_color = get_other_color(color)
    score_oppo = get_color_score(board, oppo_color)
    return score_color - score_oppo

def advanced_heuristic(board, color):
    score_color = get_color_score(board, color)
    oppo_color = get_other_color(color)
    score_oppo = get_color_score(board, oppo_color)
    # if color wins, place high value
    if score_oppo == 0:
        return 100
    # add 1 to each piece at borders
    for i in range(len(board)):
        for j in range(len(board[i])):
            if i in [0, 7] or j in [0, 7]:
                score_color += 1
    # add 1 to each piece that are protected by two or more checkers
            adj =  [(i - 1, j - 1), (i - 1, j + 1), (i + 1, j - 1), (i + 1, j + 1)]
            count = 0
            for a in adj:
                if board[a[0]][a[1]] == color:
                    count += 1
            if count >= 2:
                score_color += 1
    if len(get_possible_moves(board, color)) > len(get_possible_moves(board, oppo_color)):
        score_color += 1
    return score_color

def load_data(filename):
    checkers = []
    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            line = tuple(line)
            checkers.append(line)
    return tuple(checkers)

def write_board_to_file(board, filename):
    with open(filename, "w") as out:
        out.write(get_board_str(board))

def df_minimax_alphabeta(board, color, depth, alpha, beta):
    best_move = None
    moves = get_possible_moves(board, color)

    if not moves or depth == 0:
        return best_move, utility(board, COLOR_RED)

    if color == COLOR_RED and board in max_cache:
        cache_res = max_cache[board]
        if cache_res[1] >= depth:
            return best_move, cache_res[0]
    
    if color == COLOR_BLUE and board in min_cache:
        cache_res = min_cache[board]
        if cache_res[1] >= depth:
            return best_move, cache_res[0]

    if color == COLOR_RED:
        val = -100000
    else:
        val = 100000

    for move in moves:
        nxt_pos = get_result_board(board, move)
        nxt_color = get_other_color(color) 
        nxt_move, nxt_val = df_minimax_alphabeta(nxt_pos, nxt_color, depth - 1, alpha, beta)
        # EXPLORED_STATES[nxt_pos] = nxt_val
        if color == COLOR_RED:
            if val < nxt_val:
                val, best_move = nxt_val, move
            if val >= beta:
                break
            alpha = max(alpha, val)
        if color == COLOR_BLUE:
            if val > nxt_val:
                val, best_move = nxt_val, move
            if val <= alpha:
                break
            beta = min(beta, val)

    # update max cache 
    if color == COLOR_RED:
        max_cache[board] = (val, depth)
    if color == COLOR_BLUE:
        min_cache[board] = (val, depth)
    
    return best_move, val

if __name__ == "__main__":

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    board = load_data(input_file)

    i = 20
    best_move, val = df_minimax_alphabeta(board, COLOR_RED, i, -100000, 100000)
    print(f"finished running depth {i}, best move is {best_move}")
    result_board = get_result_board(board, best_move)
    
    write_board_to_file(result_board, output_file)
