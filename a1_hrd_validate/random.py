# def find_successor(hrd):
#     e1, e2 = find_empty_coords(hrd)
#     successor_states = []
#
#     # swap with single 1*1 neighbors
#     for e in [e1, e2]:
#         nbs = find_single_neighbors(e)
#         for n in nbs:
#             state = swap_single(hrd, e, n)
#             if state:
#                 successor_states.append(state)
#
#     # swap with 1*2 and 2*2 neighbors
#     nbs = find_single_neighbors(e1) + find_single_neighbors(e2)
#     nbs.remove(e1)
#     nbs.remove(e2)
#     for n in nbs:
#         rep = find_upper_left(hrd, n)
#         if rep[0] == e1:
#             if rep[0]
#
#     return successor_states
#
# def swap_two_two(hrd, n, e1, e2):
#     if e1[0] == e2[0] and n[0] != e1[0]: # empty in same row; check 2*2
#
# def swap_single(hrd, c, e):
#     hrd = hrd.copy()
#     if if_valid_coord(c) and hrd[c[0]][c[1]] == 7 and hrd[e[0]][e[1]] == 0:
#         hrd[c[0]][c[1]], hrd[e[0]][e[1]] = hrd[e[0]][e[1]], hrd[c[0]][c[1]]
#         return hrd
#     else:
#         return



#
# def find_single_neighbors(coord):
#     dir_to_nbs = {"down": (coord[0]+1, coord[1]),
#            "up": (coord[0]-1, coord[1]),
#            "right": (coord[0], coord[1]+1),
#            "left": (coord[0], coord[1]-1)}
#     for k in dir_to_nbs:
#         if not _if_valid_coord(dir_to_nbs[k]):
#             dir_to_nbs.pop(k)
#     return dir_to_nbs
#
#
# def _if_adjacent(coord1, coord2):
#     return (coord1[0] == coord2[0] and abs(coord1[1]-coord2[1]) <= 1) \
#            or (coord1[1] == coord2[1] and abs(coord1[0]-coord2[0]) <= 1)
#
