################################################################################
# boardLogic.py
#
# This file contains all of the logic needed to generate the board. Originally,
# the board was hardcoded, but there was a very strong attempt to convert the
# board generation to use a modified Kruskal's algorithm. If the board is still
# hardcoded, that means the attempt fell short.
#
# Name: Connor Frank
# Andrew ID: connorf
################################################################################

import boardObjs


def genBoard(board):
    pacmanStart = int(board.rows * (4 / 5)), board.cols // 2
    ghostStart = int(board.rows * (2 / 5)), board.cols // 2
    ghostStart = 5, 8
    hardcoded = [
        [-1] * 17,
        [-1, 2, 1, 1, 1, 1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 2, -1],
        [-1, 1, -1, -1, -1, 1, 1, 1, -1, 1, 1, 1, -1, -1, -1, 1, -1],
        [-1, 1, -1, -1, -1, 1, -1, 1, 1, 1, -1, 1, -1, -1, -1, 1, -1],
        [-1, 2, 1, 1, 1, 1, -1, -1, 0, -1, -1, 1, 1, 1, 1, 2, -1],
        [-1, -1, 1, -1, -1, 0, 0, 0, 0, 0, 0, 0, -1, -1, 1, -1, -1],
        [-1, -1, 1, 0, 0, 0, -1, -1, -1, -1, -1, 0, 0, 0, 1, -1, -1],
        [-1, -1, 1, -1, -1, 0, -1, 0, 0, 0, -1, 0, -1, -1, 1, -1, -1],
        [42, 0, 1, 0, 0, 0, -1, 0, 0, 0, -1, 0, 0, 0, 1, 0, 42],
        [-1, -1, 1, -1, -1, 0, -1, -1, -1, -1, -1, 0, -1, -1, 1, -1, -1],
        [-1, -1, 1, -1, -1, 0, 0, 0, 3, 0, 0, 0, -1, -1, 1, -1, -1],
        [-1, 2, 1, 1, -1, 0, -1, -1, -1, -1, -1, 0, -1, 1, 1, 2, -1],
        [-1, 1, -1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, -1, 1, -1],
        [-1, 1, -1, -1, 0, -1, -1, -1, 0, -1, -1, -1, 0, -1, -1, 1, -1],
        [-1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, -1],
        [-1] * 17,
    ]
    for i in range(board.rows):
        if i not in board.adjList:
            board.adjList[i] = dict()
        row = []
        for j in range(board.cols):
            val = hardcoded[i][j]
            if val >= 0:
                if j not in board.adjList[i]:
                    board.adjList[i][j] = set()
                for dRow in range(-1, 2):
                    for dCol in range(-1, 2):
                        if (dRow == 0 and dCol == 0) or (
                            dRow != 0 and dCol != 0
                        ):
                            continue
                        try:
                            if hardcoded[i + dRow][j + dCol] >= 0:
                                board.adjList[i][j].add((i + dRow, j + dCol))
                        except IndexError:
                            # needed b/c the teleportation point val is 42
                            pass
            if val == 42:
                row.append(boardObjs.Teleportation())
            elif val == -1:
                row.append(boardObjs.Wall(board))
            elif val == 0:
                row.append(boardObjs.Empty())
            elif val == 1:
                row.append(boardObjs.Food(board))
                board.foodCount += 1
            elif val == 2:
                row.append(boardObjs.MagicFood(board))
                board.foodCount += 1
            elif val == 3:
                row.append(boardObjs.Fruit(board))
        board.board.append(row)
    # returns starting row/col for pacman and ghosts
    return pacmanStart, ghostStart
