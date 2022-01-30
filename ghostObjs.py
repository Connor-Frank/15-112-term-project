################################################################################
# ghostObjs.py
#
# This file contains all the ghost objects. Each type of ghost has a unique
# method called "nextMove" that returns the row and column of its next move.
#
# Name: Connor Frank
# Andrew ID: connorf
################################################################################

import math
import random


class Ghost(object):
    def __init__(self, board, jailed=True, jailTime=10):
        # generic ghost
        self.color = "yellow"  # never used in-game so same color as pacman
        self.row, self.col = board.ghostStarting
        self.prevRow, self.prevCol = 0, 0
        self.nextRow, self.nextCol = 0, 0
        self.jailed = jailed
        self.jailTime = jailTime

    def getValidMoves(self, board):
        moves = board.adjList[self.row][self.col]
        # if (self.prevRow, self.prevCol) in moves:
        #     moves.remove((self.prevRow, self.prevCol))
        return moves

    def resetJailTime(self, time=10):
        self.jailed = True
        self.jailTime = time


class Random(Ghost):
    def __init__(self, board, jailed=True, jailTime=0):
        super().__init__(board, jailed=jailed, jailTime=jailTime)
        self.color = "red"

    def nextMove(self, board, app):
        _ = app  # just to show it's unused
        move = self.prevRow, self.prevCol
        while move == (self.prevRow, self.prevCol):
            move = random.choice(list(self.getValidMoves(board)))
        return move


# static distance function
def distance(x0, y0, x1, y1):
    return ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5


class Greedy(Ghost):
    def __init__(self, board, jailed=True, jailTime=10):
        super().__init__(board, jailed=jailed, jailTime=jailTime)

    # gets the closest valid move that the ghost can take to get to its goal
    def getClosestMove(self, board, goalRow, goalCol):
        best = math.inf
        bestMove = self.row, self.col
        for possibleMove in self.getValidMoves(board):
            row, col = possibleMove
            dist = distance(row, col, goalRow, goalCol)
            if dist < best and (row, col) != (self.prevRow, self.prevCol):
                best = dist
                bestMove = row, col
        return bestMove

    # gets the furthest valid move that the ghost can take to get to its goal
    def getFarthestMove(self, board, goalRow, goalCol):
        best = 0
        bestMove = self.row, self.col
        for possibleMove in self.getValidMoves(board):
            row, col = possibleMove
            dist = distance(row, col, goalRow, goalCol)
            if dist > best and (row, col) != (self.prevRow, self.prevCol):
                best = dist
                bestMove = row, col
        return bestMove


class GreedyFront(Greedy):
    # each greedy ghost has a different jailTime because that's the start value
    # if they go to jail later, their jailTime is set to 10
    def __init__(self, board, jailed=True, jailTime=20):
        super().__init__(board, jailed=jailed, jailTime=jailTime)
        # the colors of the greedy ghosts are canonically correct
        self.color = "pink"

    def nextMove(self, board, app):
        dRow, dCol = app.pacmanDir
        # extrapolates 2 units in front of the player and aims there
        goalRow = app.pacmanRow + (2 * dRow)
        goalCol = app.pacmanCol + (2 * dCol)
        if app.ghostEater:
            # farthest move if the player can eat ghosts
            return self.getFarthestMove(board, goalRow, goalCol)
        else:
            # otherwise, closest move
            return self.getClosestMove(board, goalRow, goalCol)


class GreedyAt(Greedy):
    def __init__(self, board, jailed=True, jailTime=30):
        super().__init__(board, jailed=jailed, jailTime=jailTime)
        self.color = "cyan"

    def nextMove(self, board, app):
        # aims at the player
        goalRow = app.pacmanRow
        goalCol = app.pacmanCol
        if app.ghostEater:
            return self.getFarthestMove(board, goalRow, goalCol)
        else:
            return self.getClosestMove(board, goalRow, goalCol)


class GreedyBehind(Greedy):
    def __init__(self, board, jailed=True, jailTime=40):
        super().__init__(board, jailed=jailed, jailTime=jailTime)
        self.color = "orange"

    def nextMove(self, board, app):
        dRow, dCol = app.pacmanDir
        # extrapolates 2 units behind the player and aims there
        goalRow = app.pacmanRow - (2 * dRow)
        goalCol = app.pacmanCol - (2 * dCol)
        if app.ghostEater:
            return self.getFarthestMove(board, goalRow, goalCol)
        else:
            return self.getClosestMove(board, goalRow, goalCol)
