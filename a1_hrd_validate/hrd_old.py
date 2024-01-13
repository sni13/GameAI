from typing import List, Tuple
from heapq import heappush, heappop
import sys

board_to_id = {}
id_to_board = {}
id_counter = 0
board_to_id_dfs = {}
id_to_board_dfs = {}
id_counter_dfs = 0
number_to_res = {7: 4, 0: 0, 1: 1}


CODE_EMPTY = "empty"
CODE_1x1 = "1x1"
CODE_1x2 = "1x2"
CODE_2x2 = "2x2"


class FrontierNode:
    def __init__(self, sequence: List[int], g):
        self.sequence = sequence
        self.g = g
        self.h = get_original_heuristic(get_board_by_id(sequence[-1]))
        self.f = self.g + self.h

    def __lt__(self, other):
        return self.f < other.f


class DfsFrontierNode:
    def __init__(self, sequence: List[int]):
        self.sequence = sequence


# A implementation of Priority Queue
class PriorityQueue:
    def __init__(self):
        self.queue: List[FrontierNode] = []

    def push(self, item):
        heappush(self.queue, item)

    def pop(self):
        return heappop(self.queue)

    def is_empty(self):
        return len(self.queue) == 0

class HrdBoard(object): # each Hrd board is a state
    def __init__(self, hrd):
        self.hrd = hrd
        self.pieces = []
        self.transform_to_board()

    def __str__(self):
        res = ""
        for i in self.pieces:
            res += ("\n" + str(i))
        return res

    def transform_to_board(self):
        for i in range(5):
            row = self.hrd[i]
            for j in range(4):
                c = row[j]
                if c == 0 or c == 7:
                    self.pieces.append(Piece(c, (i, j), (i, j)))
                elif c == 1: # 2*2 pieces
                    if (i+1) <= 4 and (j+1) <=3 and \
                            self.hrd[i+1][j]==self.hrd[i][j+1]==self.hrd[i+1][j+1] == 1:
                        self.pieces.append(Piece(1, (i, j), (i + 1, j + 1)))
                elif 2 <= c <=6:  # 1*2 pieces
                    if _if_valid_coord((i + 1, j)) and self.hrd[i + 1][j] == c: # vertical
                        self.pieces.append(Piece(c, (i, j), (i + 1, j), "v"))
                        number_to_res[c] = 3
                    elif _if_valid_coord((i, j + 1)) and self.hrd[i][j + 1] == c: # horizontal
                        self.pieces.append(Piece(c, (i, j), (i, j + 1), "h"))
                        number_to_res[c] = 2

    def get_successors(self):
        suc = []
        empty = []
        for p in self.pieces:
            if p.number == 0:
                empty.append(p.start)
        for p in self.pieces:
            suc.extend(get_piece_successors(p, empty, self.hrd))

        return suc


class Piece(object):
    def __init__(self, number, start, end, orient=None):
        self.number = number
        self.start = start  #upper_left rep
        self.end = end # bottom_right rep
        if orient:
            self.orient = orient

    def __str__(self):
        res = "piece #" + str(self.number) + " " + str(self.start) + " to " + str(self.end)
        if 2 <= self.number <= 6:
            res += " with orientation - " + self.orient
        return res


def get_piece_successors(piece, empty_pcs, hrd): #empty_pcs list of two coordinate tuples
    res = []
    if piece.number == 7:
        r, c = piece.start[0], piece.start[1]
        for d in ["up", "down", "left", "right"]:
            r2, c2 = get_moved_coord((r, c), d)  # move from (r,c) to (r2, c2)
            if (r2, c2) in empty_pcs:
                res.append(swap(hrd, (r, c), (r2, c2)))
    elif piece.number == 1:
        r, c = piece.start[0], piece.start[1]
        adj = {"up": [0, 2], "down": [1, 3], "left": [0, 1], "right": [2, 3]}
        for d in ["up", "down", "left", "right"]:
            coords = [(r, c), (r+1, c), (r, c+1), (r+1, c+1)] #upper left, bottom left, upper right, bottom right
            coords_adj = [coords[adj[d][0]], coords[adj[d][1]]]
            for i in range(4):
                if not i in adj[d]:
                    coords_adj.append(coords[i])
            moved_coords = []
            for coord in coords_adj:
                moved_coords.append(get_moved_coord(coord, d))

            if not (-1, -1) in moved_coords:
                if moved_coords[0] in empty_pcs and moved_coords[1] in empty_pcs:
                    res.append(move(hrd, coords, moved_coords))

    elif 2 <= piece.number <= 6:
        coord = [piece.start, piece.end]
        adj = {"up": {"v": coord, "h": coord},
               "down": {"v": [piece.end, piece.start], "h": coord},
               "left": {"v": coord, "h": coord},
               "right": {"v": coord, "h": [piece.end, piece.start]}}

        for d in ["up", "down", "left", "right"]:
            orient = piece.orient
            coords = adj[d][orient]

            moved_coords = []
            for coord in coords:
                moved_coords.append(get_moved_coord(coord, d))

            if not (-1, -1) in moved_coords:
                if orient == 'v':
                    if (d in ["up", "down"] and moved_coords[0] in empty_pcs) \
                            or (d in ["left", "right"] and moved_coords[0] in empty_pcs and moved_coords[1] in empty_pcs):
                        res.append(move(hrd, coords, moved_coords))
                elif orient == "h":
                    if (d in ["up", "down"] and moved_coords[0] in empty_pcs and moved_coords[1] in empty_pcs) \
                            or (d in ["left", "right"] and moved_coords[0] in empty_pcs):
                        res.append(move(hrd, coords, moved_coords))
    return res


def move(hrd, coords, moved_coords):
    tmp = hrd
    if len(coords) > 0:
        tmp = swap(hrd, coords[0], moved_coords[0])
        if len(coords) > 1:
            tmp = move(tmp, coords[1:], moved_coords[1:])
    return tmp


def swap(hrd, coord1, coord2):
    res = ()
    for i in range(len(hrd)):
        row = ()
        for j in range(len(hrd[i])):
            if (i, j) == coord1:
                row += (hrd[coord2[0]][coord2[1]],)
            elif (i, j) == coord2:
                row += (hrd[coord1[0]][coord1[1]],)
            else:
                row += (hrd[i][j],)
        res += (row,)
    return res


def get_moved_coord(coord, direction):
    r, c = coord[0], coord[1]
    if direction == "up" and _if_valid_coord((r-1, c)):
        return r-1, c
    elif direction == "down" and _if_valid_coord((r+1, c)):
        return r + 1, c
    elif direction == "left" and _if_valid_coord((r, c - 1)):
        return r, c - 1
    elif direction == "right" and _if_valid_coord((r, c + 1)):
        return r, c + 1
    else:
        return -1, -1


def _if_valid_coord(coord):
    return 0 <= coord[0] <= 4 and 0 <= coord[1] <= 3


def add_board_id_pair(board):
    global id_counter
    if board not in board_to_id:
        board_to_id[board] = id_counter
        id_to_board[id_counter] = board
        id_counter += 1


def get_id_by_board(board):
    if board not in board_to_id:
        add_board_id_pair(board)
    return board_to_id[board]


def get_board_by_id(bid):
    return id_to_board[bid]


def add_board_id_pair_dfs(board):
    global id_counter_dfs
    if board not in board_to_id_dfs:
        board_to_id_dfs[board] = id_counter_dfs
        id_to_board_dfs[id_counter_dfs] = board
        id_counter_dfs += 1


def get_board_by_id_dfs(bid):
    return id_to_board_dfs[bid]


def get_id_by_board_dfs(board):
    if board not in board_to_id_dfs:
        add_board_id_pair_dfs(board)
    return board_to_id_dfs[board]


def get_piece_type(val):
    if val == 0:
        return CODE_EMPTY
    elif val == 1:
        return CODE_2x2
    elif 2 <= val <= 6:
        return CODE_1x2
    elif val == 7:
        return CODE_1x1
    else:
        assert(False)


def if_goal_state(board):
    return board[3][1] == board[3][2] == board[4][1] == board[4][2] == 1


def load_data(filename):
    hrd = []

    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            line = tuple(int(x) for x in line)
            hrd.append(line)

    return tuple(hrd)


def get_successors(board):
    state = HrdBoard(board)
    return state.get_successors()


def get_cost(sequence):
    return len(sequence)


def get_mahattan_heuristic(board):
    distance = -1
    for row in range(len(board)):
        for col in range(len(board[row])):
            val = board[row][col]
            if get_piece_type(val) == CODE_2x2:
                distance = abs(row - 3) + abs(col - 1)
    return distance


def get_original_heuristic(board):
    md = get_mahattan_heuristic(board)
    if md <= 1:
        return md
    else:
        return md+3


def astar(start_board, output):
    f = open(output, "w")
    frontier = PriorityQueue()
    frontier.push(FrontierNode([get_id_by_board(start_board)], 0))

    while not frontier.is_empty():
        curr_node = frontier.pop()
        curr_board = get_board_by_id(curr_node.sequence[-1])
        successors = get_successors(curr_board)
        for successor in successors:
            if not successor in board_to_id:
                successor_id = get_id_by_board(successor)

                new_sequence = curr_node.sequence + [successor_id]
                if if_goal_state(successor):
                    f.write(f"Cost of the solution: {str(len(new_sequence) - 1)}\n")
                    for step in new_sequence:
                        for row in get_board_by_id(step):
                            convert = ""
                            for i in row:
                                convert += str(number_to_res[i])
                            f.write(convert+"\n")
                        f.write("\n")
                    return

                new_node = FrontierNode(new_sequence, curr_node.g + 1)
                frontier.push(new_node)
    f.close()


def dfs(start_board, output):
    f = open(output, "w")
    frontier = []
    frontier.append(DfsFrontierNode([get_id_by_board_dfs(start_board)]))

    while not len(frontier) == 0:
        curr_node = frontier.pop()
        curr_board = get_board_by_id_dfs(curr_node.sequence[-1])
        successors = get_successors(curr_board)
        for successor in successors:
            if not successor in board_to_id_dfs:
                successor_id = get_id_by_board_dfs(successor)

                new_sequence = curr_node.sequence + [successor_id]
                if if_goal_state(successor):
                    f.write(
                        f"Cost of the solution: {str(len(new_sequence) - 1)}\n")
                    for step in new_sequence:
                        for row in get_board_by_id_dfs(step):
                            convert = ""
                            for i in row:
                                convert += str(number_to_res[i])
                            f.write(convert+"\n")
                        f.write("\n")
                    return

                new_node = DfsFrontierNode(new_sequence)
                frontier.append(new_node)
    f.close()



if __name__ == "__main__":
    # input_file = sys.argv[1]
    # output_dfs = sys.argv[2]
    # output_astar = sys.argv[3]
    input_file = "hrd_input.txt"
    output_astar = "hrd_output_own.txt"
    output_dfs = "hrd_dfs.txt"

    start_board = load_data(input_file)
    astar(start_board, output_astar)
    dfs(start_board, output_dfs)
