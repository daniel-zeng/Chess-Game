import copy

pieceTypes = ("pawn", "king", "queen", "bishop", "knight", "rook")

CHECKMATE = "CHK"
ENPASSANT = "ENP"
CONSOLE = "CON"
GUI = "GUI"
ROWCO = "RCL"
KSCAST = "KSC"
QSCAST = "QSC"
white = "w"
black = "b"
castlingPlaces = ((7, 4, 7, 6), (7, 4, 7, 2), (0, 4, 0, 6), (0, 4, 0, 2))

movement = {
    "n": [
        (1, 2),
        (2, 1),
        (-1, 2),
        (-2, 1),
        (1, -2),
        (2, -1),
        (-1, -2),
        (-2, -1)
    ],
    "r": [
        (1, 0),
        (0, 1),
        (-1, 0),
        (0, -1)
    ],
    "b": [
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1)
    ],
}
pieces = "KRBNQP"


### board manipulation and input utilities ###


def listAllValidMoves(player, board, speshuls, isCheck):
    moves = allMovesinPieces(player, board, speshuls, "combo")
    validmoves = []
    for piece, pos, move in moves:
        if isValidMove(player, pos, move, piece, board, speshuls):
            validmoves.append((piece, pos, move))
    if not isCheck:
        if player == white:
            if speshuls[1] and verifyCastling(KSCAST, board, speshuls):
                validmoves.append(KSCAST)
            if speshuls[2] and verifyCastling(QSCAST, board, speshuls):
                validmoves.append(QSCAST)
        else:
            if speshuls[3] and verifyCastling(KSCAST, board, speshuls):
                validmoves.append(KSCAST)
            if speshuls[4] and verifyCastling(QSCAST, board, speshuls):
                validmoves.append(QSCAST)
    return validmoves


def allMovesinPieces(player, board, speshuls, mode):
    allPiece_Pos = getAllPieces(player, board)
    return getAllMoveInPieces(player, allPiece_Pos, board, speshuls, mode)


def isCheck(board, speshuls, isGUI):
    # get all moves for other player
    otherMoves = allMovesinPieces(other(speshuls[0]), board, speshuls, "combo" if isGUI else "list")

    # get current king
    king, king_pos = selectPieces("K" if speshuls[0] == white else "k", board)[0]

    if isGUI:
        for piece, piece_pos, move in otherMoves:
            if king_pos == move:
                return (piece_pos, move)
        return False
    else:
        return king_pos in otherMoves


def isValidMove(player, start, end, piece, board, speshuls):
    # make a copy move and verify if king in danger
    originR, originC = start

    hypotBoard = copy.deepcopy(board)

    hypotBoard[originR][originC] = 0
    hypotBoard[end[0]][end[1]] = piece

    return not isCheck(hypotBoard, speshuls, False)


def applyMove(val, board, speshuls):
    if val == KSCAST or val == QSCAST:
        applyCastling(val, board, speshuls)
    else:
        selected, start, target_coord = val
        # print(val)
        applyNormal(board, target_coord, start, selected, speshuls)

    # apply fullmove
    if speshuls[0] == black:
        speshuls[8] += 1

    # swap player
    speshuls[0] = other(speshuls[0])


def applyNormal(board, end, start, piece, speshuls):
    # no error checking cuz speed, redundancy
    targetOrig = board[end[0]][end[1]]
    originR, originC = start

    # apply halfmove
    applyHalfmove(piece.lower() == "p", targetOrig != 0, speshuls)

    # apply promotion
    if speshuls[6]:
        piece = speshuls[6].upper() if piece.isupper() else speshuls[6]
        speshuls[6] = None

    board[originR][originC] = 0
    board[end[0]][end[1]] = piece

    # empassant capture
    if piece.lower() == "p" and end == speshuls[5]:
        board[originR][end[1]] = 0

    # specials checking
    applyNormalSpecials(end, start, piece, speshuls, targetOrig != 0 and targetOrig.lower() == "r")


def applyNormalSpecials(end, start, piece, speshuls, captureRook):
    if piece.lower() == "p" and abs(end[0] - start[0]) == 2:
        # add empassant square
        speshuls[5] = (start[0] + (1 if piece == "p" else -1), start[1])
    else:
        speshuls[5] = None

    # modify castling rights
    if piece == "K":
        speshuls[1] = False
        speshuls[2] = False
    elif piece == "k":
        speshuls[3] = False
        speshuls[4] = False

    if piece == "R":
        if start == (7, 0):
            speshuls[2] = False
        elif start == (7, 7):
            speshuls[1] = False
    elif piece == "r":
        if start == (0, 0):
            speshuls[4] = False
        elif start == (0, 7):
            speshuls[3] = False

    if captureRook:
        if end == (7, 0):
            speshuls[2] = False
        elif end == (7, 7):
            speshuls[1] = False
        elif end == (0, 0):
            speshuls[4] = False
        elif end == (0, 7):
            speshuls[3] = False


def applyCastling(val, board, speshuls):
    row = None

    # apply halfmove
    applyHalfmove(False, False, speshuls)

    # Apply castling rights
    if speshuls[0] == white:
        speshuls[1] = False
        speshuls[2] = False
        row = 7
    else:
        speshuls[3] = False
        speshuls[4] = False
        row = 0

    # Applying castling to the board
    board[row][4] = 0
    if val == KSCAST:
        board[row][5] = "R" if speshuls[0] == white else "r"
        board[row][6] = "K" if speshuls[0] == white else "k"
        board[row][7] = 0
    else:
        board[row][0] = 0
        board[row][1] = 0
        board[row][2] = "K" if speshuls[0] == white else "k"
        board[row][3] = "R" if speshuls[0] == white else "r"


def applyHalfmove(isPawn, isCapture, speshuls):
    if isPawn or isCapture:
        speshuls[7] = 0
    else:
        speshuls[7] += 1


def verifyCastling(val, board, speshuls):
    row = None
    if speshuls[0] == white:
        row = 7
        if val == KSCAST and not speshuls[1]:
            return False
        if val == QSCAST and not speshuls[2]:
            return False

    else:
        row = 0
        if val == KSCAST and not speshuls[3]:
            return False
        if val == QSCAST and not speshuls[4]:
            return False

    # check open slots
    if val == KSCAST:
        checkOpen = [(row, 5), (row, 6)]
    else:
        checkOpen = [(row, 2), (row, 3)]

    for coord in checkOpen:
        r, c = coord
        if board[r][c]:
            return False

        # check if these open positions are under possible check
        hypotBoard = copy.deepcopy(board)
        hypotBoard[row][4] = 0
        hypotBoard[r][c] = "K" if speshuls[0] == white else "k"
        if isCheck(hypotBoard, speshuls, False):
            return False

    return True


# returns the final valid Piece, move for apply move
def inputLoopProcessor(player, mode, board, speshuls, isCheck):
    while 1:
        val = processAlgebraic(player, mode, board, speshuls)
        if not val:
            print("Invalid input, try again")
            continue

        # ignore special (ie castling) cases for now
        if val == KSCAST or val == QSCAST:
            if isCheck:
                print("Invalid move: King is under check")
                continue

            if verifyCastling(val, board, speshuls):
                return val
            print("Invalid move: Castling cannot be made")
            continue

        piece, target_coord, typeT, disc = val
        possiblePieces = selectPiecesRC(piece.upper() if player == white else piece.lower(), board, typeT, disc)
        prunedPieces = []
        for pce, pos in possiblePieces:
            placesCanMove = getMoves(player, pce.lower(), pos[0], pos[1], board, speshuls)
            if target_coord in placesCanMove:
                prunedPieces.append((pce, pos))

        if len(prunedPieces) > 1:
            print("Disambiguating moves, try again")
            continue
        if len(prunedPieces) == 0:
            print("No", piece, "can reach that square, try again")
            continue

        selected, pos = prunedPieces[0]

        if selected.lower() == "p" and (target_coord[0] == 0 or target_coord[0] == 7) and not speshuls[6]:
            print("Invalid move: please specify promotion piece")
            continue

        if isValidMove(player, pos, target_coord, selected, board, speshuls):
            return selected, pos, target_coord
        else:
            print("Invalid move: either under checkmate or other")


def processAlgebraic(player, mode, board, speshuls):
    while 1:
        print("\n")
        res = input(("White" if player == white else "Black") + "> ")
        ret = algebraicToRC(res, player, board, speshuls)
        if ret:
            return ret
        else:
            print("Invalid input, try again")


# returns list of piece pos tuple
def getAllPieces(player, board):
    q = []
    for row in range(8):
        for col in range(8):
            if board[row][col] and owner(board[row][col]) == player:
                q.append((board[row][col], (row, col)))
    return q


def getAllMoveInPieces(player, piece_and_pos, board, speshuls, mode):
    totalMoves = []
    for piece, pos in piece_and_pos:
        if mode == "list":
            totalMoves.extend(getMoves(player, piece.lower(), pos[0], pos[1], board, speshuls))
        elif mode == "combo":
            for move in getMoves(player, piece.lower(), pos[0], pos[1], board, speshuls):
                totalMoves.append((piece, pos, move))
    return totalMoves


def selectPiecesRC(piece, board, typeT=None, disc=None):
    getPos = lambda item: item[1]
    getRow = lambda item: item[1][0]
    getCol = lambda item: item[1][1]

    existing = selectPieces(piece, board)
    if not typeT:
        return existing
    q = []
    for item in existing:
        if isinstance(disc, tuple):
            if getPos(item) == disc:
                q.append(item)
        elif isinstance(disc, int):
            if typeT == "row":
                if getRow(item) == disc:
                    q.append(item)
            elif typeT == "col":
                if getCol(item) == disc:
                    q.append(item)
            else:
                print("improper usage")
        else:
            print("improper usage")
    return q


# list of (piece, pos tuples)
def selectPieces(piece, board):
    q = []
    for row in range(8):
        for col in range(8):
            if board[row][col] and board[row][col] == piece:
                q.append((board[row][col], (row, col)))
    return q


def standardBoard():
    order = "rnbqkbnr"
    board = [list(order),
             ["p"] * 8,
             [0] * 8,
             [0] * 8,
             [0] * 8,
             [0] * 8,
             ["P"] * 8,
             list(order.upper()),
             ]

    return board


def printBoard(b, doRoCo, doAlg):
    if doRoCo:
        print(" ", end=" ")
        for i in range(8):
            print(i, end=" ")
    print()
    start = 0
    for row in b:
        if doRoCo:
            print(start, end=" ")
        for item in row:
            if item:
                print(item, end=" ")
            else:
                print("-", end=" ")
        if doAlg:
            print(rankToRow(start), end=" ")
        start += 1
        print()
    if doAlg:
        print(" ", end=" ")
        for i in range(8):
            print(colToFile(i), end=" ")


###### piece board abstraction ######
def owner(pce):
    assert isinstance(pce, str)
    if pce.isupper():
        return white
    return black


def other(player):
    return white if player == black else black


def fenRepresentation(board, speshuls):
    fen = ""
    count = 0
    for row in range(8):
        for col in range(8):
            if not board[row][col]:
                count += 1
            else:
                if count:
                    fen += str(count)
                    count = 0
                fen += board[row][col]
        if count:
            fen += str(count)
            count = 0
        if row != 7:
            fen += "/"
    fen += " "
    fen += "w" if speshuls[0] == white else "b"
    fen += " "
    if speshuls[1] or speshuls[2] or speshuls[3] or speshuls[4]:
        if speshuls[1]:
            fen += "K"
        if speshuls[2]:
            fen += "Q"
        if speshuls[3]:
            fen += "k"
        if speshuls[4]:
            fen += "q"
    else:
        fen += "-"
    fen += " "

    if speshuls[5]:
        fen += colToFile(speshuls[5][1]) + str(rowToRank(speshuls[5][0]))
    else:
        fen += "-"
    fen += " {} {}".format(speshuls[7], speshuls[8])

    return fen


###### piece movement logic ######
def getMoves(player, piece, row, col, board, speshuls):
    q = []
    assert piece.islower()
    if piece == "p":
        moveTwo = None
        direct = -1 if player == white else 1

        moveOne = (row + direct, col)
        if canMoveToGeneral(player, moveOne[0], moveOne[1], True, board):
            q.append(moveOne)

            # cuz can only moveTwo if can move one
            if player == white and row == 6 or player == black and row == 1:
                moveTwo = (row + direct * 2, col)
                if canMoveToGeneral(player, moveTwo[0], moveTwo[1], True, board):
                    q.append(moveTwo)

        # capture cases:
        leftCap = (moveOne[0], col - 1)
        rightCap = (moveOne[0], col + 1)
        if canMoveToPwnCap(player, leftCap[0], leftCap[1], board, speshuls):
            q.append(leftCap)
        if canMoveToPwnCap(player, rightCap[0], rightCap[1], board, speshuls):
            q.append(rightCap)

    elif piece == "k":
        for dir in movement["r"] + movement["b"]:
            if canMoveToGeneral(player, row + dir[0], col + dir[1], False, board):
                q.append((row + dir[0], col + dir[1]))
    elif piece == "n":
        for jump in movement[piece]:
            new_r = row + jump[0]
            new_c = col + jump[1]
            if canMoveToGeneral(player, new_r, new_c, False, board):
                q.append((new_r, new_c))
    elif piece == "r" or piece == "b":
        for dir in movement[piece]:
            q += canMoveToRecursive(player, row + dir[0], col + dir[1], dir[0], dir[1], board)
    elif piece == "q":
        for dir in movement["r"] + movement["b"]:
            q += canMoveToRecursive(player, row + dir[0], col + dir[1], dir[0], dir[1], board)
    return q


def canMoveToGeneral(player, r_new, c_new, is_pawn, board):
    if not inBounds(r_new, c_new):
        return False

    piece = board[r_new][c_new]
    if piece == 0:
        return True

    if owner(piece) == player:
        return False

    return not is_pawn


def canMoveToRecursive(player, r_new, c_new, dr, dc, board):
    if not inBounds(r_new, c_new):
        return []

    piece = board[r_new][c_new]
    if piece == 0:
        return [(r_new, c_new)] + canMoveToRecursive(player, r_new + dr, c_new + dc, dr, dc, board)
    elif owner(piece) != player:
        return [(r_new, c_new)]
    return []


def canMoveToPwnCap(player, r_new, c_new, board, speshuls):
    if not inBounds(r_new, c_new):
        return False

    # empassant case
    if (r_new, c_new) == speshuls[5]:
        return True

    piece = board[r_new][c_new]
    if piece == 0:
        return False

    return owner(piece) != player


def inBounds(r, c):
    assert isinstance(r, int) and isinstance(c, int)
    if c < 0 or c > 7:
        return False
    if r < 0 or r > 7:
        return False
    return True


###### algebraic selection logic ######

def algebraicToRC(alg, player, board, speshuls):
    if alg == "0-0" or alg == "O-O":
        return KSCAST
    elif alg == "0-0-0" or alg == "O-O-O":
        return QSCAST
    else:
        isCapture = "x" in alg
        alg = alg.replace("x", "").replace("+", "").replace("#", "")

        if len(alg) < 2:
            return False
        piece = None

        # pawn promotion case
        if "=" in alg or alg[-1].lower() in "rbnq":
            alg = alg.replace("=", "")
            speshuls[6] = alg[-1].lower()
            alg = alg[:-1]
            print(alg, speshuls[6])
        else:
            speshuls[6] = None

        if len(alg) < 2:
            return False

        # get target square
        target = alg[-2:]
        alg = alg[:-2]

        target_coords = processTS(target)
        if not target_coords:
            return False

        typeT = None
        disc = None

        if len(alg) == 0:
            if isCapture:
                return False

            return "p", target_coords, None, None
        elif len(alg) == 1:
            first = alg[0]
            if first.islower():
                # pawn move with discriminator
                piece = "p"
                typeT = "col"
                disc = fileToCol(first)
                if disc not in range(8):
                    return False
            else:
                if first not in pieces:
                    return False
                piece = first.lower()

            return piece, target_coords, typeT, disc
        elif len(alg) == 2 or len(alg) == 3:
            # Piece selector and discriminator
            first, second = alg[0], alg[1:]
            piece = first.lower()
            typeT, disc = processDisc(second)
            if not typeT:
                return False
            assert disc in range(8) or disc[0] in range(8) and disc[1] in range(8)
            return piece, target_coords, typeT, disc
        else:
            return False


def processDisc(inpt):
    if len(inpt) == 1:
        if inpt.isalpha():
            if inpt not in validFirst:
                return False, None
            return "col", fileToCol(inpt)
        elif inpt.isdigit():
            inpt = int(inpt)
            if inpt not in range(1, 9):
                return False, None
            return "row", rankToRow(inpt)
        else:
            return False, None
    else:
        select_coord = processTS(inpt)
        if not select_coord:
            return False, None

        return "rowcol", select_coord


# returns false if not valid target square selector
validFirst = "abcdefgh"


def processTS(selection):
    first, second = selection
    if first.isalpha() and second.isdigit():
        first = first.lower()
        second = int(second)
        if first not in validFirst or second not in range(1, 9):
            return False
        row = rankToRow(second)
        col = fileToCol(first)

        return row, col
    else:
        return False


def rankToRow(inpt):
    return 8 - inpt


def fileToCol(inpt):
    return ord(inpt) - 97


def rowToRank(inpt):
    return rankToRow(inpt)


def colToFile(inpt):
    return chr(97 + inpt)
