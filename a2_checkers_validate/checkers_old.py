
COLOR_RED = "r"
COLOR_RED_KING = "R"
COLOR_BLUE = "b"
COLOR_BLUE_KING = "B"
EMPTY = "."
MOVE_REG = "M"
MOVE_JUMP = "J"
COLOR_TO_OPPONENT = {"r": "b", "b": "r"}

max_cache = {
    # key: tuple[tuple]: (val, depth)
}
min_cache = {}

def switch_player(color):
    if color == "r":
        return "b"
    else:
        return "r"


def actions(board, color):
    moves = []
    for i in range(len(board)):
        row = board[i]
        for j in range(len(row)):
            if board[i][j].lower() == color:
                adj = find_adjacent(board, i, j)
                for a in adj:
                    x, y = a
                    if board[x][y] == EMPTY: # adjacent space is empty
                        moves.append(("M", (i, j), (x, y)))
                    elif board[x][y].lower() == COLOR_TO_OPPONENT[color]: # opponent
                        # multi_move = multiple_jump(board, color, (i, j), (x, y))
                        jump_x, jump_y = jump_pos(("J", (i, j), (x, y)))
                        if _if_valid_coord(jump_x, jump_y) and \
                                board[jump_x][jump_y] == EMPTY:
                            moves.append(("J", (i, j), (x, y)))
                        # if suc:
                            # res.append((MOVE_JUMP, suc))
    return moves

def filter_actions(board, color, moves):
    res = []
    for m in moves:
        if m[0] == MOVE_JUMP:
            res.extend(multi_jump(board, m, color))
        else:
            res.append([m])  
    return res

def multi_jump(board, m, color): # list of all possible seq of multi-jumps
    new_board = res_move(board, m)
    jump_to = jump_pos(m)
    new_board_actions = actions(new_board, color)
    jumps_seq = []

    for a in new_board_actions:
        if a[0] == "J" and a[1] == jump_to:
            for seq in multi_jump(new_board, a, color):
                jumps_seq.append([m] + seq)
    if jumps_seq == []:
        return [[m]]
    else:
        return jumps_seq


def jump_pos(move):
    i, j = move[1]
    x, y = move[2]
    delta_x, delta_y = x - i, y - j
    new_pos = x + delta_x, y + delta_y
    return new_pos

def res_move(board, move):
    type = move[0]
    i, j = move[1]
    x, y = move[2]
    if type == "M":
        return swap(board, (i, j), (x, y))
    elif type == "J":
        return jump(board, (i, j), (x, y))

def result(board, moves):
    # moves are from func actions
    if len(moves) == 1:
        return res_move(board, moves[0])
    else:
        curr = board
        for m in moves:
            curr = res_move(curr, m)
        return curr

def find_adjacent(board, i, j):
    piece = board[i][j]
    up = [(i - 1, j - 1), (i - 1, j + 1)]
    down = [(i + 1, j - 1), (i + 1, j + 1)]
    adj = []

    if piece.lower() == COLOR_RED: #up
        adj = up.copy()
        if piece.isupper():
            adj.extend(down.copy())
    elif piece.lower() == COLOR_BLUE: #down
        adj = down.copy()
        if piece.isupper():
            adj.extend(up.copy())
    ooi = []
    for k in range(len(adj)):
        if not _if_valid_coord(adj[k][0], adj[k][1]):
            ooi.append(k)
    cp = []
    for p in range(len(adj)):
        if p not in ooi:
            cp.append(adj[p])

    return cp


def _if_valid_coord(x, y):
    return 0 <= x <= 7 and 0 <= y <= 7


def swap(board, piece, empty):
    res = ()
    p = board[piece[0]][piece[1]]
    if (empty[0] == 0 and p == COLOR_RED) or (
            empty[0] == 7 and p == COLOR_BLUE):  # if not king, upgrade it
        p = p.upper()
    for i in range(len(board)):
        row = ()

        for j in range(len(board[i])):
            if (i, j) == piece:
                row += (EMPTY,)
            elif (i, j) == empty:
                row += (p,)
            else:
                row += (board[i][j],)
        res += (row,)
    return res


def jump(board, player, opponent):
    delta = (opponent[0] - player[0], opponent[1] - player[1])
    pos = (opponent[0] + delta[0], opponent[1] + delta[1])
    piece = board[player[0]][player[1]]
    res = ()

    if (pos[0] == 0 and piece == COLOR_RED) or (
            pos[0] == 7 and piece == COLOR_BLUE):  # if not king, upgrade it
        piece = piece.upper()

    if board[pos[0]][pos[1]] != EMPTY:
        return
    for i in range(len(board)):
        row = ()
        for j in range(len(board[i])):
            if (i, j) in [opponent, player]:
                row += (EMPTY,)
            elif (i, j) == pos:
                row += (piece,)
            else:
                row += (board[i][j],)
        res += (row,)
    return res


def terminal(board, color):
    return value(board, COLOR_RED) == 0 or value(board, COLOR_BLUE) == 0 or \
        actions(board, color) == []


def board_to_str(board):
    res = ''
    for row in board:
        for piece in row:
            res += piece
        res += '\n'
    return res


def value(board, color):
    lower = 0
    upper = 0
    for row in board:
        for i in row:
            if i == color.lower():
                lower += 1
            elif i == color.upper():
                upper += 1
    return upper * 2 + lower * 1


def utility(board, color):
    v_c = value(board, color)
    o = COLOR_TO_OPPONENT[color]
    v_o = value(board, o)
    return v_c - v_o

def minimax_val(board):
    return utility(board, COLOR_RED)

def load_data(filename):
    checkers = []
    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            line = tuple(line)
            checkers.append(line)
    return tuple(checkers)



def df_minimax(board, color, depth):
    best_move = None
    val = 0
    if terminal(board, color) or depth == 0:
        return best_move, utility(board, color)

    if color == COLOR_RED:
        val = -100000
    elif color == COLOR_BLUE:
        val = 100000
    moves = actions(board, color)
    filtered_moves = filter_actions(board, color, moves)
    for move in filtered_moves:
        nxt_pos = result(board, move)
        nxt_color = switch_player(color) 
        nxt_move, nxt_val = df_minimax(nxt_pos, nxt_color, depth-1)
        if color == COLOR_RED and val < (-nxt_val):
            val, best_move = -nxt_val, move
        if color == COLOR_BLUE and val > (-nxt_val):
            val, best_move = -nxt_val, move
    return best_move, val

def df_minimax_alphabeta(board, color, depth, alpha, beta):
    best_move = None
    if terminal(board, color) or depth == 0:
        return best_move, minimax_val(board)

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

    moves = actions(board, color)
    filtered_moves = filter_actions(board, color, moves)
    for move in filtered_moves:
        nxt_pos = result(board, move)
        nxt_color = switch_player(color) 
        nxt_move, nxt_val = df_minimax_alphabeta(nxt_pos, nxt_color, depth-1, alpha, beta)
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
    if val == 1:
        print("depth: ", depth, "val: ", val, color, "\n" + board_to_str(result(board, best_move)) )
    return best_move, val

def main(board, output_file):
    #starts from "r"
    # for i in range(10, 21):
        i=20
        print(f"running depth {i}")
        best_move, val = df_minimax_alphabeta(board, COLOR_RED, i, -100000, 100000)
        nxt_move = result(board, best_move)
        print(board_to_str(nxt_move), "utility: ", val)

if __name__ == "__main__":
    # input_file = sys.argv[1]
    # output_file = sys.argv[2]
    # input_file = "terminal_test2.txt"
    input_file = "input0.txt"
    output_file = "output0.txt"

    # start board
    start_board = load_data(input_file)
    print(board_to_str(start_board), "utility: ", utility(start_board, 'r'))
    # a = actions(start_board, "b")
    # print(a)
    # print(filter_actions(start_board, "b", a))
    main(start_board, output_file)
