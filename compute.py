from board_utils import *
import copy
import random
from math import inf


class Compute:
    #updated piece values from genetic paper
    value = {
        'k': 90000,
        'q': 1710,
        'r': 824,
        'n': 521,
        'b': 572,
        'p': 100
    }
    #Piece square tables from sunfish
    usePst = True
    pst = {
        'p': (0, 0, 0, 0, 0, 0, 0, 0,
              78, 83, 86, 73, 102, 82, 85, 90,
              7, 29, 21, 44, 40, 31, 44, 7,
              -17, 16, -2, 15, 14, 0, 15, -13,
              -26, 3, 10, 9, 6, 1, 0, -23,
              -22, 9, 5, -11, -10, -2, 3, -19,
              -31, 8, -7, -37, -36, -14, 3, -31,
              0, 0, 0, 0, 0, 0, 0, 0),
        'n': (-66, -53, -75, -75, -10, -55, -58, -70,
              -3, -6, 100, -36, 4, 62, -4, -14,
              10, 67, 1, 74, 73, 27, 62, -2,
              24, 24, 45, 37, 33, 41, 25, 17,
              -1, 5, 31, 21, 22, 35, 2, 0,
              -18, 10, 13, 22, 18, 15, 11, -14,
              -23, -15, 2, 0, 2, 0, -23, -20,
              -74, -23, -26, -24, -19, -35, -22, -69),
        'b': (-59, -78, -82, -76, -23, -107, -37, -50,
              -11, 20, 35, -42, -39, 31, 2, -22,
              -9, 39, -32, 41, 52, -10, 28, -14,
              25, 17, 20, 34, 26, 25, 15, 10,
              13, 10, 17, 23, 17, 16, 0, 7,
              14, 25, 24, 15, 8, 25, 20, 15,
              19, 20, 11, 6, 7, 6, 20, 16,
              -7, 2, -15, -12, -14, -15, -10, -10),
        'r': (35, 29, 33, 4, 37, 33, 56, 50,
              55, 29, 56, 67, 55, 62, 34, 60,
              19, 35, 28, 33, 45, 27, 25, 15,
              0, 5, 16, 13, 18, -4, -9, -6,
              -28, -35, -16, -21, -13, -29, -46, -30,
              -42, -28, -42, -25, -25, -35, -26, -46,
              -53, -38, -31, -26, -29, -43, -44, -53,
              -30, -24, -18, 5, -2, -18, -31, -32),
        'q': (6, 1, -8, -104, 69, 24, 88, 26,
              14, 32, 60, -10, 20, 76, 57, 24,
              -2, 43, 32, 60, 72, 63, 43, 2,
              1, -16, 22, 17, 25, 20, -13, -6,
              -14, -15, -2, -5, -1, -10, -20, -22,
              -30, -6, -13, -11, -16, -11, -16, -27,
              -36, -18, 0, -19, -15, -15, -21, -38,
              -39, -30, -31, -13, -31, -36, -34, -42),
        'k': (4, 54, 47, -99, -99, 60, 83, -62,
              -32, 10, 55, 56, 56, 55, 10, 3,
              -62, 12, -57, 44, -67, 28, 37, -31,
              -55, 50, 11, -4, -19, 13, 0, -49,
              -55, -43, -52, -28, -51, -47, -8, -50,
              -47, -42, -43, -79, -64, -32, -29, -32,
              -4, 3, -14, -50, -57, -18, 13, 4,
              17, 30, -3, -14, 6, -1, 40, 18),
    }
    hash_value = {
        'k': 1,
        'q': 2,
        'r': 3,
        'n': 4,
        'b': 5,
        'p': 6,
        'K': 7,
        'Q': 8,
        'R': 9,
        'N': 10,
        'B': 11,
        'P': 12
    }

    def __init__(self, ci):
        self.ci = ci

    def calcMove(self):
        self.current_eval = self.evalPce(self.ci.board)

        self.processQ = []
        self.counter = 0
        self.breakCounter = 0
        next_move, score = self.findMove(-inf, inf, self.ci.board, self.ci.speshuls, 1, False)
        return next_move

    maxDepth = 4
    skipProb = 0

    #added alphabeta
    def findMove(self, a, b, board, speshuls, depth, eval_only):

        currentPlayer = speshuls[0]
        # if we hit depth, return eval
        if depth == Compute.maxDepth:
            return self.evalPce(board)

        # get current state
        inCheck = isCheck(board, speshuls, False)
        current_moves = listAllValidMoves(speshuls[0], board, speshuls, inCheck)
        if 1:
            random.shuffle(current_moves)

        if len(current_moves) == 0:
            ret = 0
            #checkmate case
            if inCheck:
                ret = Compute.value['k'] if currentPlayer == black else -Compute.value['k']
            if eval_only:
                return ret
            return None, ret


        # initialization
        bestMove = None
        bestScore = None

        numTested = 0
        alpha = a
        beta = b
        for move in current_moves:
            numTested += 1
            if len(current_moves) > 4:
                #skip probabality
                if random.random() < Compute.skipProb and numTested != len(current_moves) - 1:
                    continue

            # go over each move, and apply it to a copy of the board
            cboard = copy.deepcopy(board)
            cspeshuls = copy.copy(speshuls)

            if move[0].lower() == "p" and (move[2][0] == 0 or move[2][0] == 7):
                cspeshuls[6] = 'q'
            applyMove(move, cboard, cspeshuls)

            score = self.findMove(alpha, beta, cboard, cspeshuls, depth + 1, True)
            if score is None:
                continue
                print(depth + 1)

            if currentPlayer == white:  # max
                if bestScore is None or score > bestScore:
                    bestScore = score
                    bestMove = move
                    alpha = max(alpha, bestScore)

            else:
                if bestScore is None or score < bestScore:
                    bestScore = score
                    bestMove = move
                    beta = min(beta, bestScore)

            if beta <= alpha:
                self.breakCounter += 1
                break  # alpha/beta cut off

        if bestScore is None:
            print(depth, len(current_moves), current_moves)

        if not eval_only:
            return (bestMove, bestScore)
        return bestScore

    def evalPce(self, board):
        total = 0
        for row in range(8):
            for col in range(8):
                pce = board[row][col]
                if not pce: continue
                scale = 1 if pce.isupper() else -1
                pos = row * 8 + col if pce.isupper() else (7 - row) * 8 + (7 - col)
                pstVal = Compute.pst[pce.lower()][pos]
                val = Compute.value[pce.lower()] + pstVal if Compute.usePst else 0
                total += val * scale
        return total

    def lazyHash(self, board):
        total = 0
        mult = 1
        for row in range(8):
            for col in range(8):
                pce = board[row][col]
                if not pce: continue
                total += Compute.hash_value[pce] * mult
                mult *= 13
        return total
