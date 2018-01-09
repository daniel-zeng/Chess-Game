from board_utils import *
from compute import *
from gui import *
import subprocess, time


class ChessInstance:
    debugChess = False
    sf_getprompt = 'isready'
    sf_done = 'readyok'

    def __init__(self, mode, stockfish=None, cust_ai=None):
        self.board = standardBoard()
        self.speshuls = [white] + [True] * 4 + [None] * 2 + [0] + [1]
        # 5 is empassant
        # 6 is pawn upgrade
        # 7 is halfmove, 8 is fullmove
        self.mode = mode

        self.stockfish = stockfish
        self.custom_ai = cust_ai

        if self.stockfish:
            self.loadStockfish()
            self.initStockfish()

        if self.stockfish == self.speshuls[0]:
            self.doStockfish(False)

        if self.custom_ai:
            self.loadCust()

        if self.custom_ai == self.speshuls[0]:
            self.doCust()

    def loadCust(self):
        self.cust = Compute(self)

    def loadStockfish(self):
        import platform
        sys_name = platform.system()
        proc_name = None
        procStrings = {
            'Windows': 'stockfish_8_x64.exe',
            'Darwin': 'stockfish-8-64',
            'Linux': 'stockfish_8_x64'
        }
        if sys_name in procStrings:
            proc_name = procStrings[sys_name]
        else:
            print("Your system is not supported")
            exit(1)
        try:
            self.engine = subprocess.Popen(
                proc_name,
                universal_newlines=True,
                bufsize=1,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
        except FileNotFoundError as e:
            print("Please put", proc_name, "in the root directory.")
            exit(1)

    def initStockfish(self):
        self.engine.stdout.readline().strip()
        self.put('uci')
        self.put('setoption name Hash value 128')
        self.put('setoption name Threads value 4')
        self.put('setoption name Minimum Thinking Time value 300')
        self.put('ucinewgame')

    def put(self, command):
        if ChessInstance.debugChess: print(">", command)
        self.engine.stdin.write(command + '\n')

    def get(self):
        self.put(ChessInstance.sf_getprompt)
        bestmove = None
        if ChessInstance.debugChess: print('<')
        while True:
            text = self.engine.stdout.readline().strip()
            if ChessInstance.debugChess: print("\t" + text)
            if text == ChessInstance.sf_done:
                break
            if text.startswith("bestmove"):
                bestmove = text
        return bestmove

    def startGame(self):
        if self.mode == CONSOLE:
            self.consoleGame()
        elif self.mode == GUI:
            self.guiGame()

    def guiGame(self):
        gui = ChessGUI(75, self)

    def submitMove(self, val):
        applyMove(val, self.board, self.speshuls)

        if self.stockfish == self.speshuls[0]:
            self.doStockfish(False)
        if self.custom_ai == self.speshuls[0]:
            self.doCust()

        isCheckk, validmoves = self.checkAndValidMoves(True)

        print(fenRepresentation(self.board, self.speshuls))

        return isCheckk, validmoves

    def checkAndValidMoves(self, isGUI=False):
        isCheckk = isCheck(self.board, self.speshuls, True)
        validmoves = listAllValidMoves(self.speshuls[0], self.board, self.speshuls, isCheckk)
        return isCheckk, validmoves

    def consoleGame(self):
        while True:
            isCheckk, validmoves = self.checkAndValidMoves()

            if len(validmoves) == 0:
                if isCheckk:
                    print("Checkmate", "white" if self.speshuls[0] == white else "black")
                else:
                    print("Stalemate")
                break

            if isCheckk:
                print("You are under check,", "white" if self.speshuls[0] == white else "black")

            printBoard(self.board, True, True)
            val = inputLoopProcessor(self.speshuls[0], self.mode, self.board, self.speshuls, isCheckk)

            print(fenRepresentation(self.board, self.speshuls))

            applyMove(val, self.board, self.speshuls)

            if self.stockfish == self.speshuls[0]:
                self.doStockfish()
            if self.custom_ai == self.speshuls[0]:
                self.doCust()

    def stockfishMove(self, start, end, prin=True):
        if prin:
            printBoard(self.board, True, True)
            print()
            print()

        selected = self.board[start[0]][start[1]]
        if selected.lower() == "k" and (start[0], start[1], end[0], end[1]) in castlingPlaces:
            applyCastling(KSCAST if end[1] == 6 else QSCAST, self.board, self.speshuls)
        else:
            applyNormal(self.board, end, start, selected, self.speshuls)

        if self.speshuls[0] == black:
            self.speshuls[8] += 1

        self.speshuls[0] = other(self.speshuls[0])

    def doStockfish(self, prin=True):
        fen = fenRepresentation(self.board, self.speshuls)
        self.put('position fen ' + fen)
        self.put('go')
        time.sleep(0.1)
        val = None
        while val is None:
            time.sleep(0.1)
            val = self.get()
        move = val.split()[1]
        if prin: print("stockfish", move)
        if move == "(none)":
            print("Checkmate/Stalemate!")
            printBoard(self.board, True, True)
            exit()
        start, end, promo = processTS(move[:2]), processTS(move[2:4]), move[4:]
        if promo:
            self.speshuls[6] = promo
        self.stockfishMove(start, end, prin)

    def doCust(self):
        move = self.cust.calcMove()
        if move is None:
            return isCheck(self.board, self.speshuls, False), None
        if move[0].lower() == "p" and (move[2][0] == 0 or move[2][0] == 7):
            self.speshuls[6] = 'q'
        applyMove(move, self.board, self.speshuls)
