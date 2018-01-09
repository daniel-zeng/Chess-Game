from chess_instance import white, black, GUI, CONSOLE, ChessInstance

def main():
    prompt()

    val, stockfish, useCustom = processInput()
    assert not(stockfish and useCustom)
    print()

    c = ChessInstance(val, stockfish, useCustom)
    c.startGame()

def prompt():
    print("Chess! Please enter your the input mode:")
    print("1) Algebraic notation (Console)")
    print("2) GUI selection")
    print("/s To toggle Stockfish")
    print("/c To toggle Custom Engine")
    print("/h for help")
    print("/q to quit")


def processInput():
    useStockfish = False
    useCustom = False
    while 1:
        inpt = input("> ")
        if inpt == "/h":
            print("1) Algebraic: https://en.wikipedia.org/wiki/Algebraic_notation_(chess)")
            print("2) GUI: Select pieces using the GUI.")
        elif inpt == "/q":
            exit()
        elif inpt == "1":
            print("You are using Algebraic notation")
            return CONSOLE, useStockfish, useCustom
        elif inpt == "2":
            print("You are using GUI selection")
            return GUI, useStockfish, useCustom

        if inpt == "/s" or (inpt == "/c" and useStockfish):
            useStockfish = False if useStockfish else processPlayer()
            print("You are {}using Stockfish.".format("" if useStockfish else "no longer "))
        if inpt == "/c" or (useCustom and inpt == "/s"):
            useCustom = False if useCustom else processPlayer()
            print("You are {}using Custom Engine.".format("" if useCustom else "no longer "))

        if inpt not in "1 2 /h /q /s /c".split():
            print("Input not understood, try again")
            print("Your options are: 1 2 /h /q /s /c")


def processPlayer():
    print("Play as white or black? (b/w):")
    while 1:
        inpt = input("> ")
        if inpt == "b":
            print("You are playing as black")
            return white
        elif inpt == "w":
            print("You are playing as white")
            return black
        else:
            print("Input not understood, try again")
            print("Your options are: b w")

if __name__ == '__main__':
    main()