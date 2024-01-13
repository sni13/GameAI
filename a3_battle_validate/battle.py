import sys, random
from heapq import heappush, heappop

WATER = "0"
SUBMARINE = "1"
DESTROYER = "2"
CRUISER = "3"
BATTLESHIP = "4"

BOARD_SIZE = 0 

name_hash = {}
counter = 1


class Variable: 
    def __init__(self, row, col, domain=[]):
        '''Create a variable object, specifying its row, col, domain (optional)
        '''
        self.row = row
        self.col = col
        self.dom = list(domain)         #Make a copy of passed domain
        self.curdom = [True] * len(domain)      #using list
        #for bt_search
        self.assignedValue = None

    def domain(self):
        '''return the variable's PERMANENTdomain'''
        return(list(self.dom))
    
    def prune_value(self, value):
        '''Remove value from CURRENT domain'''
        self.curdom[self.value_index(value)] = False

    def unprune_value(self, value):
        '''Restore value to CURRENT domain'''
        self.curdom[self.value_index(value)] = True

    def value_index(self, value):
        '''Domain values need not be numbers, so return the index
           in the domain list of a variable value'''
        return self.dom.index(value)

    def cur_domain(self):
        '''return list of values in CURRENT domain (if assigned 
           only assigned value is viewed as being in current domain)'''
        vals = []
        # if self.is_assigned():
        #     vals.append(self.get_assigned_value())
        # else:
        for i, val in enumerate(self.dom):
            if self.curdom[i]:
                vals.append(val)
        return vals
    
    def is_assigned(self):
        return self.assignedValue != None
    
    def assign(self, value):
        self.assignedValue = value

    def unassign(self):
        self.assignedValue = None
    
    def get_assigned_value(self):
        return self.assignedValue

    def restore_curdom(self):
        for i in range(len(self.curdom)):
            self.curdom[i] = True

    def prune_cur_doamin(self, d):
        for i in range(len(self.curdom)):
            if self.dom[i] != d:
                self.curdom[i] = False

    def __str__(self):
        return("row-{} col-{} dom-{}".format(self.row, self.col, self.dom))

class Constraint:
    def __init__(self, name, scope, priority, limit=None ): 
        self.scope = list(scope)  # list of Variable objs
        self.name = name
        self.limit = limit
        self.priority = priority
        # if not self.check():
        #     for s in self.scope:
        #         if not s.is_assigned():
        #             s.assign(0)

    def check(self):
        if self.name == "r" or self.name == "c":
            count = 0
            for v in self.scope:
                if v.is_assigned():
                    val = v.get_assigned_value()
                    if int(val) != 0:
                        count += 1
            return count == self.limit
        elif self.name.isnumeric(): # number of ships
            count = 0
            coords = []
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    v = self.scope[i][j] 
                    val = v.get_assigned_value()
                    if val and val == int(self.name):
                        count += 1
                        coords.append((i, j))
            if count > (self.limit * int(self.name)):
                return False
            if self.name == "1" and count == self.limit:
                return True
            ships = get_consecutive(coords, int(self.name))
            if not check_valid_consecutive(ships):
                return False
            for s in ships:
                if len(s) > int(self.name): #oversized consecutive
                    return False
            return len(ships) == self.limit
        elif self.name == "b":
            v = self.scope[0]
            if v.is_assigned():
                v_val = v.get_assigned_value()
                if v_val == 0:
                    return True
                for a in self.scope[1:]:
                    a_val = a.get_assigned_value()
                    if a_val and not (a_val == v_val or a_val == 0):
                        return False
                return True

    def get_n_unasgn(self):
        '''return the number of unassigned variables in the constraint's scope'''
        n = 0
        unassigned = None
        if self.name.isnumeric():
            for row in self.scope:
                for v in row:
                    if not v.is_assigned():
                        unassigned = v
                        n += 1
        else:
            for v in self.scope:
                if not v.is_assigned():
                    unassigned = v
                    n = n + 1
        return n, unassigned

    def __lt__(self, other):
        return self.priority < other.priority

    def __str__(self):
        return("name-{} scope-{} limit-{}".format(self.name, len(self.scope), self.limit))

def get_consecutive(coords, n): 
    """get list of ships for type "n" ship
    input coords are the coords with number "n"
    """
    res = []
    while len(coords) > 0:
        (x, y) = coords[0]
        sub = [(x, y)]
        dir = ""
        coords.remove((x, y))
        for incre in range(1, n):
            if dir == "":
                if (x, y + incre) in coords:
                    dir = "h"
                elif (x + incre, y) in coords:
                    dir = "v"
            if dir == "h":
                if (x, y + incre) in coords:
                    sub.append((x, y + incre))
                    coords.remove((x, y + incre))
            else:
                if (x + incre, y) in coords:
                    sub.append((x + incre, y))
                    coords.remove((x + incre, y))
        res.append(sub)
    return res

def check_valid_consecutive(lst_of_consec):
    n = len(lst_of_consec)
    for i in range(n-1):
        l, r = lst_of_consec[i], lst_of_consec[i+1]
        for p in l:
            for j in r:
                if if_adj(p, j):
                    return False
    return True

def if_adj(coord1, coord2):
    x, y = coord1
    a, b = coord2
    if x == a:
        return abs(y-b) == 1
    elif y == b:
        return abs(x-a) == 1
    elif abs(x-a) <= 1 and abs(y-b) <= 1:
        return True
    else:
        return False


class CSP: 
    def __init__(self, vars=[], cons=[]):
        '''a CSP object'''
        self.vars = []
        self.cons = []
        self.vars_to_cons = dict()
        self.add_vars(vars)
        for c in cons:
            self.add_con(c)

    def add_vars(self, vars):
        for row in vars:
            sub = []
            for v in row:
                sub.append(v)
                self.vars_to_cons[v] = []
            self.vars.append(row)

    def add_con(self, c):
        for i in c.scope:
            if isinstance(i, list):
                for v in i:
                    if v in self.vars_to_cons:
                        self.vars_to_cons[v].append(c)
            else:
                v = i
                if v in self.vars_to_cons:
                    self.vars_to_cons[v].append(c)
        self.cons.append(c)
    
    def get_cons_with_var(self, var):
        return list(self.vars_to_cons[var])
    
    def print_soln(self):
        res_str = ""
        res_str += "CSP Assignments = \n"
        for row in self.vars:
            r = ""
            for v in row:
                if not v.is_assigned():
                    r = r + "X"
                else:
                    r = r + str(v.get_assigned_value())
            res_str += r + "\n"

        res_str += "\n"
        return res_str
    
    def get_soln(self):
        res_str = ""
        for row in self.vars:
            r = ""
            for v in row:
                if not v.is_assigned():
                    r = r + "X"
                else:
                    r = r + str(v.get_assigned_value())
            res_str += r + "\n"
        return res_str


def load_data(filename):
    global BOARD_SIZE
    with open(filename, "r") as f:
        lines = f.readlines()
        row_con = lines[0].strip()
        BOARD_SIZE = len(row_con)
        col_con = lines[1].strip()
        num_con = lines[2].strip()
        board = lines[3:]
    return board, [row_con, col_con, num_con]

def convert_board_to_vars(board):
    vars = []
    for i in range(len(board)):
        line = board[i]
        sub_vars = []
        for j in range(len(line)):
            val = board[i][j]
            domain = [0, 1, 2, 3, 4]
            if val != '0':  # no hint
                if val == 'S':
                    domain = [1]
                elif val == 'W': 
                    domain = [0]
                elif val == 'M':
                    domain = [3, 4]
                else:
                    domain = [2, 3, 4]
            v = Variable(i, j, domain)
            sub_vars.append(v)
        vars.append(sub_vars)
    return vars

def convert_to_constraints(vars, csts):
    cons = []
    row_con, col_con, num_con = csts
    # for each row, add row con
    row_con = list(int(x) for x in row_con)
    for row in range(BOARD_SIZE):
        limit = row_con[row]  # row constraint number
        scope = vars[row]
        cons.append(Constraint("r", scope, 1, limit))
    # for each col, add col con
    col_con = list(int(x) for x in col_con)
    for col in range(BOARD_SIZE):
        limit = col_con[col]
        scope = [x[col] for x in vars]
        cons.append(Constraint("c", scope, 1, limit))
    # for each ship count, add con
    num_con = list(int(x) for x in num_con)
    num_con.extend((4 - len(num_con)) * [0])  #if len(num_con) < 4: extend 0s to the end
    for i in range(len(num_con)):
        limit = num_con[i]
        scope = vars
        cons.append(Constraint(str(i + 1), scope, 3, limit))
    # for every variable, add a binary constraint:
    # every cell adjacent to it should be either 0 or equal to it
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            v = vars[i][j]
            adj = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1), \
                     (i - 1, j - 1), (i - 1, j + 1), (i + 1, j - 1), (i + 1, j + 1)]
            scope = [v]  # first var is the center
            for a in adj:
                if valid_coord(a):
                    scope.append(vars[a[0]][a[1]]) # others are adjacent cells
            cons.append(Constraint("b", scope, 2))
    return cons

def preprocess(board, csts):
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            l = []
            if board[i][j] == "S":
                l = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1), \
                     (i - 1, j - 1), (i - 1, j + 1), (i + 1, j - 1), (i + 1, j + 1)]
            elif board[i][j] == "L":
                l = [(i - 1, j), (i + 1, j), (i, j - 1), \
                     (i - 1, j - 1), (i - 1, j + 1), (i + 1, j - 1), (i + 1, j + 1)]
            elif board[i][j] == "R":
                l = [(i - 1, j), (i + 1, j), (i, j + 1), \
                     (i - 1, j - 1), (i - 1, j + 1), (i + 1, j - 1), (i + 1, j + 1)]
            elif board[i][j] == "T":
                l = [(i - 1, j), (i, j - 1), (i, j + 1), \
                     (i - 1, j - 1), (i - 1, j + 1), (i + 1, j - 1), (i + 1, j + 1)]
            elif board[i][j] == "B":
                l = [(i + 1, j), (i, j - 1), (i, j + 1), \
                     (i - 1, j - 1), (i - 1, j + 1), (i + 1, j - 1), (i + 1, j + 1)]
            for (a, b) in l:
                if valid_coord((a, b)):
                    board[a][b] = "W"
    row_con = list(int(x) for x in csts[0])
    for i in range(BOARD_SIZE):
        row = board[i]
        limit = row_con[i]
        if limit == 0:
            board[i] = ["W"] * BOARD_SIZE
        if (BOARD_SIZE - row.count("0")- row.count("W")) == limit:
            for j in range(BOARD_SIZE):
                if board[i][j] == "0":
                    board[i][j] = "W"
    col_con = list(int(x) for x in csts[1])

    for j in range(BOARD_SIZE):
        limit = col_con[j]
        count_zero = 0
        for i in range(BOARD_SIZE):
            if board[i][j] in ["0", "W"]:
                count_zero += 1
        non_zero = BOARD_SIZE - count_zero
        if limit == 0 or non_zero == limit:
            for i in range(BOARD_SIZE):
                if board[i][j] == "0":
                    board[i][j] = "W"

def valid_coord(coord):
    return 0 <= coord[0] <= (BOARD_SIZE -1) \
        and 0 <= coord[1] <= (BOARD_SIZE -1) 

class Backtracking:
    def __init__(self, csp):
        self.csp = csp
        unasgn_vars = list()
        self.nPrunings  = 0
        self.nDecisions = 0
        self.gac_queue = GACQueue()
    
    def restoreValues(self,prunings):
        for var, val in prunings:
            var.unprune_value(val)
    
    def restore_all_variable_domains(self):
        for row in self.csp.vars:
            for var in row:
                if var.is_assigned():
                    var.unassign()
                var.restore_curdom()
    
    def restoreUnasgnVar(self, var):
        self.unasgn_vars.append(var)
    
    def clear_stats(self):
        self.nDecisions = 0
        self.nPrunings = 0
        self.runtime = 0

    def print_stats(self):
        print("Search made {} variable assignments and pruned {} variable values".format(
            self.nDecisions, self.nPrunings))


    def bt_search(self, level):
        self.unasgn_vars = []
        for row in self.csp.vars:
            for var in row:
                if len(var.domain()) == 1:
                    var.assign(var.domain()[0])
                if not var.is_assigned():
                    self.unasgn_vars.append(var)

        if len(self.unasgn_vars) == 0:
            return self.csp.get_soln()
        v = self.pick_unassigned_variable()

        for d in v.cur_domain():
            v.assign(d)
            constraint_ok = True
            cons = self.csp.get_cons_with_var(v)
            for con in cons:
                n, x = con.get_n_unasgn()
                if n == 0:
                    if not con.check():
                        constraint_ok = False
            if constraint_ok == True:
                res = self.bt_search(level + 1)
                if res:
                    return res
        v.unassign()
        return

    def bt_search_fc(self, level):
        global counter

        self.unasgn_vars = []
        for row in self.csp.vars:
            for var in row:
                if len(var.domain()) == 1:
                    var.assign(var.domain()[0])
                if not var.is_assigned():
                    self.unasgn_vars.append(var)


        board_str = self.csp.print_soln()
        if board_str not in name_hash:
            name_hash[board_str] = counter
            counter += 1

        print(f"id: {name_hash[board_str]} entering {level}")
        print(board_str)


        print(f"unasgn_vars: {len(self.unasgn_vars)}")
        if len(self.unasgn_vars) == 0:
            self.csp.print_soln()
            print(f"exiting here {level}")
            return self.csp.print_soln()
        v = self.pick_unassigned_variable()
        print("curr_v:", v)
        enter_next = False

        for d in v.cur_domain():
            print("level", level, v, d)
            # if d == 2:
            #     print('good')
            v.assign(d)
            DWOoccured = False
            cons = self.csp.get_cons_with_var(v)
            for con in cons:
                n, x = con.get_n_unasgn()
                if n == 1:
                    if not self.fc_check(con, x):
                        DWOoccured = True
                        break
            if not DWOoccured:
                enter_next = True
                res = self.bt_search_fc(level+1)
                if res:
                    return res
            v.restore_curdom()

        print(f"id: {name_hash[board_str]} Enter next level: {enter_next}")

        v.unassign()
        print(f"there {level}")
        return
    
    def fc_check(self, con, x):
        for d in x.cur_domain():
            # print("fccheck: ", x.cur_domain())
            x.assign(d)
            if d == 1:
                print()
            if not con.check():
                print("prune: ", d)
                x.prune_value(d)
            x.unassign()
        if x.cur_domain() == []: 
            x.restore_curdom()
            return False
        return True  

    def pick_unassigned_variable(self):
        return self.unasgn_vars[0]

# A implementation of Priority Queue
class GACQueue:
    def __init__(self):
        self.queue = []

    def push(self, con):
        heappush(self.queue, con)

    def pop(self):
        return heappop(self.queue)

    def isInQueue(self, item):
        return item in self.queue

    def is_empty(self):
        return len(self.queue) == 0

    def empty(self):
        while not self.is_empty:
            self.pop()

def main(input_file, output_file):
    board, csts = load_data(input_file)
    board = (x.strip() for x in board)
    board = [list(x) for x in board]
    preprocess(board, csts)
    vars = convert_board_to_vars(board)
    cons = convert_to_constraints(vars, csts)
    csp = CSP(vars, cons)
    bt = Backtracking(csp)
    res = bt.bt_search(0)
    converted = convert_solution(res)
    with open(output_file, "w") as out:
        out.write(converted)
 
def get_coords(txt, num):
    init = []
    for sub in txt.split():
        init.append(list(sub))
    coords = []
    for i in range(len(init)):
        for j in range(len(init)):
            if int(init[i][j]) == num:
                coords.append((i, j))
    return coords

def convert_solution(unfilered):
    n = len(unfilered.split()[0])
    res = [['W' for _ in range(n)] for _ in range(n)]
    
    for i in range(1, 5):
        coords = get_coords(unfilered, i)
        consec = get_consecutive(coords, i)
        for c in consec:
            if i == 1:
                x, y = c[0]
                res[x][y] = "S"
                
            elif i == 2:
                x1, y1 = c[0]
                x2, y2 = c[1]
                if x1 == x2: #same row: L and R
                    res[x1][y1] = "L"
                    res[x2][y2] = "R"
                else: # assert y1 == y2
                    res[x1][y1] = "T"
                    res[x2][y2] = "B"
            elif i == 3:
                x1, y1 = c[0]
                x2, y2 = c[1]
                x3, y3 = c[2]
                if x1 == x2:
                    res[x1][y1] = "L"
                    res[x2][y2] = "M"
                    res[x3][y3] = "R"
                else:
                    res[x1][y1] = "T"
                    res[x2][y2] = "M"
                    res[x3][y3] = "B"
            else:
                x1, y1 = c[0]
                x2, y2 = c[1]
                x3, y3 = c[2]
                x4, y4 = c[3]
                if x1 == x2:
                    res[x1][y1] = "L"
                    res[x2][y2] = "M"
                    res[x3][y3] = "M"
                    res[x4][y4] = "R"
                else:
                    res[x1][y1] = "T"
                    res[x2][y2] = "M"
                    res[x3][y3] = "M"
                    res[x4][y4] = "B"
    return lst_to_str(res)

def lst_to_str(lst):
    res = ''
    for row in lst:
        for val in row:
            res = res + val
        res += "\n"
    return res


if __name__ == "__main__":
    # input_file = sys.argv[1]
    # output_file = sys.argv[2]
    input_file = "input_easy2.txt"
    output_file = "output_easy2.txt"

    # main(input_file, output_file)

    board, csts = load_data(input_file)
    board = (x.strip() for x in board)
    board = [list(x) for x in board]
    preprocess(board, csts)
    vars = convert_board_to_vars(board)
    cons = convert_to_constraints(vars, csts)
    csp = CSP(vars, cons)
    bt = Backtracking(csp)
    csp.vars[0][0].assign(0)
    csp.vars[0][1].assign(0)
    csp.vars[0][2].assign(0)
    csp.vars[0][3].assign(2)
    csp.vars[0][4].assign(2)
    csp.vars[0][5].assign(0)

    csp.vars[1][0].assign(3)
    csp.vars[1][1].assign(0)
    csp.vars[1][2].assign(0)
    csp.vars[1][3].assign(0)
    csp.vars[1][4].assign(0)
    csp.vars[1][5].assign(0)

    csp.vars[2][0].assign(3)
    csp.vars[2][1].assign(0)
    csp.vars[2][2].assign(0)
    csp.vars[2][3].assign(2)
    csp.vars[2][4].assign(2)
    csp.vars[2][5].assign(0)

    csp.vars[3][0].assign(3)
    csp.vars[3][1].assign(0)
    print(bt.bt_search_fc(0))

# 000220
# 300000
# 300220
# 30XXX0
# 000000
# X0X0X0