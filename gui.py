from tkinter import *
from PIL import ImageTk
from board_utils import owner, KSCAST, QSCAST, white, black, castlingPlaces, other


class ChessGUI:
    darkColor = "#B58863"
    lightColor = "#F0D9B5"
    dotColor = "#87c9ff"
    player = "wb"
    side = 8
    castlingLoc = {
        white + KSCAST: (7, 6),
        white + QSCAST: (7, 2),
        black + KSCAST: (0, 6),
        black + QSCAST: (0, 2),
    }
    kingSpot = ((7, 4), (0, 4))
    fixedPersp = False

    def __init__(self, leng, ci):
        self.tk = Tk()
        self.tk.title('Chess')
        self.leng = leng
        self.canvas = Canvas(self.tk, width=leng * ChessGUI.side, height=leng * ChessGUI.side,
                             highlightthickness=0)
        self.canvas.bind("<Button-1>", self.click)

        self.ci = ci
        self.firstClick = None
        self.drawnDots = []
        self.drawnChecks = []
        self.drawnPieces = []

        self.pieces = self.loadPieces()
        self.drawBoard()
        self.checkPos, self.validmoves = self.ci.checkAndValidMoves(True)
        self.drawPieces()
        self.canvas_focus = True

        self.canvas.pack(padx=30, pady=30)
        raiseTop(self.tk)
        self.tk.mainloop()

    def perspConvert(self, r, c):
        if ChessGUI.fixedPersp or self.ci.speshuls[0] == white:
            return r, c
        return ChessGUI.side - r - 1, ChessGUI.side - c - 1

    def click(self, e):
        if not self.canvas_focus:
            return

        r, c = self.perspConvert(e.y // self.leng, e.x // self.leng)
        # print(r, c)
        val = self.ci.board[r][c]
        if self.firstClick:
            # figure out if clicked is a choice dot
            self.removeChoiceDots()
            click2 = self.dotClick(r, c)
            if click2:
                # valid click
                self.firstClick = None
                if click2[0].lower() == "p" and (click2[2][0] == 0 or click2[2][0] == 7):
                    self.tk.wait_window(self.showPromotion())
                self.checkPos, self.validmoves = self.ci.submitMove(click2)

                if not self.validmoves:
                    if self.ci.stockfish == self.ci.speshuls[0] or self.ci.custom_ai == self.ci.speshuls[0]:
                        self.ci.speshuls[0] = other(self.ci.speshuls[0])

                    self.showEnd("Checkmate" if self.checkPos else "Stalemate")

                self.drawPieces()

                return

        if val and owner(val) == self.ci.speshuls[0]:
            if self.firstClick is None or self.firstClick != (r, c):
                self.firstClick = (r, c)
                self.drawChoiceDots(r, c)
            else:
                self.firstClick = None
        else:
            self.firstClick = None

    def showPromotion(self):
        top = Toplevel()
        top.title("Choose Promotion Piece")
        self.canvas_focus = False

        button = Button(top, text="Queen", command=lambda: self.promo("q", top))
        button.pack()
        button = Button(top, text="Rook", command=lambda: self.promo("r", top))
        button.pack()
        button = Button(top, text="Bishop", command=lambda: self.promo("b", top))
        button.pack()
        button = Button(top, text="Knight", command=lambda: self.promo("n", top))
        button.pack()
        return top

    def showEnd(self, msg):
        top = Toplevel()
        top.title(msg)
        self.canvas_focus = False

        button = Button(top, text="OK", command=top.destroy)
        button.pack()
        return top

    def promo(self, piece, top):
        top.destroy()
        self.canvas_focus = True
        self.ci.speshuls[6] = piece

    def dotClick(self, r, c):
        for move in self.validmoves:
            if self.firstClick == move[1] and (r, c) == move[2]:
                return move
            elif move in (KSCAST, QSCAST) and \
                    (self.firstClick[0], self.firstClick[1], r, c) in castlingPlaces:
                return move

        return False

    def drawChoiceDots(self, r, c):
        for move in self.validmoves:
            if (r, c) == move[1]:
                self.drawnDots.append(self.drawDot(move[2][0], move[2][1]))
            # castling cases:
            elif move in (KSCAST, QSCAST) and (r, c) in ChessGUI.kingSpot:
                self.drawnDots.append(self.drawDot(ChessGUI.castlingLoc[self.ci.speshuls[0] + move][0]
                                                   , ChessGUI.castlingLoc[self.ci.speshuls[0] + move][1]))

    def drawDot(self, ro, co):
        r, c = self.perspConvert(ro, co)
        dot_width = self.leng / 3.5
        x = (c + 0.5) * self.leng
        y = (r + 0.5) * self.leng

        # returns the draw object
        return self.canvas.create_oval(x - dot_width / 2, y - dot_width / 2, x + dot_width / 2, y + dot_width / 2,
                                       fill=ChessGUI.dotColor, width=0)

    def drawCheck(self):
        check1R, check1C = self.perspConvert(self.checkPos[0][0], self.checkPos[0][1])
        check2R, check2C = self.perspConvert(self.checkPos[1][0], self.checkPos[1][1])
        dot_width = self.leng * 0.9
        x = (check1C + 0.5) * self.leng
        y = (check1R + 0.5) * self.leng

        # returns the draw object
        self.drawnChecks.append(
            self.canvas.create_oval(x - dot_width / 2, y - dot_width / 2, x + dot_width / 2, y + dot_width / 2,
                                    fill=None, width=self.leng * 0.03, outline="red"))
        x = (check2C + 0.5) * self.leng
        y = (check2R + 0.5) * self.leng

        # returns the draw object
        self.drawnChecks.append(
            self.canvas.create_oval(x - dot_width / 2, y - dot_width / 2, x + dot_width / 2, y + dot_width / 2,
                                    fill=None, width=self.leng * 0.03, outline="red"))

    def removeCheck(self):
        while self.drawnChecks:
            self.canvas.delete(self.drawnChecks.pop())

    def removeChoiceDots(self):
        while self.drawnDots:
            self.canvas.delete(self.drawnDots.pop())

    def loadPieces(self):
        names = "krbnqp"
        dir = "img/"
        pieces = {}
        for p in ChessGUI.player:
            for n in names:
                filen = "{}{}{}.png".format(dir, p, n)
                try:
                    pieces[p + n] = ImageTk.PhotoImage(file=filen, width=self.leng, height=self.leng)
                except IOError as e:
                    print(e)
                    exit(1)
        return pieces

    def drawPieces(self):
        while self.drawnPieces:
            self.canvas.delete(self.drawnPieces.pop())

        for rowP in range(ChessGUI.side):
            for colP in range(ChessGUI.side):
                val = self.ci.board[rowP][colP]
                row, col = self.perspConvert(rowP, colP)
                if val:
                    player = white if val.isupper() else black
                    pce = self.canvas.create_image((col + .5) * self.leng, (row + .5) * self.leng,
                                                   image=self.pieces[player + val.lower()], anchor="center")
                    self.drawnPieces.append(pce)

        self.removeCheck()
        if self.checkPos:
            self.drawCheck()

    def drawBoard(self):
        isLight = True
        for row in range(ChessGUI.side):
            for col in range(ChessGUI.side):
                self.canvas.create_rectangle(col * self.leng, row * self.leng,
                                             (col + 1) * self.leng, (row + 1) * self.leng,
                                             fill=(ChessGUI.lightColor if isLight else ChessGUI.darkColor),
                                             width=0)
                if col != ChessGUI.side - 1:
                    isLight = not isLight


def raiseTop(window):
    window.update()
    window.attributes('-topmost', 1)
    window.attributes('-topmost', 0)
