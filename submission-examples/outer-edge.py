# reading the width and the height
w, h = map(int, input().split())
# declaring the board variable (a w by h matrix)
board = [[0 for x in range(w)] for y in range(h)]

def read_board():
    # accessing the global variable board
    global board
    # iterating over all lines of the input
    for i in range(h):
        # saving the lines as lists of integers
        board[i] = list(map(int, input().split()))

# reading the initial board position
read_board()
while True:
    # going from the top left corner to the top right one
    for _ in range(w - 1):
        print("r")
        # each turn reading the new board position
        read_board()
    # going from the top right corner to the bottom right one
    for _ in range(h-1):
        print("d")
        # each turn reading the new board position
        read_board()
    # going from the bottom right corner to the bottom left one
    for _ in range(w-1):
        print("l")
        # each turn reading the new board position
        read_board()
    # going from the bottom left corner to the top left one
    for _ in range(h-1):
        print("u")
        # each turn reading the new board position
        read_board()
