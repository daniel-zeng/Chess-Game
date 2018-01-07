from board_utils import *

class Compute:
    value = {
        'k': 90000,
        'q': 900,
        'r': 500,
        'n': 300,
        'b': 300,
        'p': 100
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
        print(self.lazyHash(self.ci.board))
        print(self.evalPce(self.ci.board))


        #get current state
        isCheckk, validmoves = self.ci.validMoves()
        for move in validmoves:
            pass


    def evalPce(self, board):
        total = 0
        for row in range(8):
            for col in range(8):
                pce = self.ci.board[row][col]
                if not pce: continue
                scale = 1 if pce.isupper() else -1
                total += Compute.value[pce.lower()] * scale
        return total


    def lazyHash(self, board):
        total = 0
        mult = 1
        for row in range(8):
            for col in range(8):
                pce = self.ci.board[row][col]
                if not pce: continue
                total += Compute.hash_value[pce] * mult
                mult *= 13
        return total