################################################################################
# boardObjs.py
#
# This file contains all of the objects that pertain to the game board,
# including the board itself. Every object on the board has a point value
# associated with it, and this point value is interpreted by the logic found
# in "main.py".
#
# Name: Connor Frank
# Andrew ID: connorf
################################################################################

import boardLogic


class Board(object):
    def __init__(self, width, height, cellSize):
        self.rows = height // cellSize
        if self.rows % 2 == 0:
            self.rows -= 1
        self.cols = width // cellSize
        if self.cols % 2 == 0:
            self.cols -= 1
        # if these are still 16 and 17, i failed making board generation
        self.rows = 16
        self.cols = 17

        self.cellSize = cellSize
        self.board = []
        self.foodCount = 0
        self.adjList = dict()
        pacmanStarting, self.ghostStarting = boardLogic.genBoard(self)
        self.startRow, self.startCol = pacmanStarting

    # magic method to index a board object
    def __getitem__(self, index):
        return self.board[index]

    # ditto for len(app.board)
    def __len__(self):
        return len(self.board)

    # gets the center of a row and column in the board
    def getCenter(self, row, col, margin):
        x = margin + self.cellSize // 2 + (self.cellSize * col)
        y = margin + self.cellSize // 2 + (self.cellSize * row)
        return x, y


# generic BoardObj, overridden and inherited all over the place
class BoardObj(object):
    def __init__(self, pointVal):
        self.size = 0
        self.pointVal = pointVal


# teleportation block
class Teleportation(BoardObj):
    def __init__(self):
        super().__init__(42)


# wall block
class Wall(BoardObj):
    def __init__(self, board):
        super().__init__(-1)
        self.size = board.cellSize // 2


# empty block
class Empty(BoardObj):
    def __init__(self):
        super().__init__(0)


# pieces of food
class Food(BoardObj):
    def __init__(self, board, pointVal=1):
        super().__init__(pointVal)
        self.size = board.cellSize // 10


# magic pieces of food that let you eat ghosts
class MagicFood(Food):
    def __init__(self, board):
        super().__init__(board, pointVal=2)
        self.size = board.cellSize // 4


# fruits (currently only cherries but i might add more, we'll see)
class Fruit(BoardObj):
    def __init__(self, board):
        super().__init__(pointVal=100)
        self.size = board.cellSize
