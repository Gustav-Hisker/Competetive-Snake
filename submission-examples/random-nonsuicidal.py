from random import choice

# reading the width and the height
w, h = map(int, input().split())
# declaring the board variable (a w by h matrix)
board = [[0 for _ in range(w)] for _ in range(h)]

def read_board():
    # accessing the global variable board
    global board
    # iterating over all lines of the input
    for i in range(h):
        # saving the lines as lists of integers
        board[i] = list(map(int, input().split()))

# function to get the coordinates of the head of the snake this program controls
def find_head():
    global board
    # iterating over all fields on the board
    for i in range(h):
        for j in range(w):
            # returning the cords if the head was found
            if board[i][j] == 1:
                return j, i

# repeating forever (until the program gets terminated)
while True:
    # reading the current state of the board
    read_board()

    # getting heads position
    x, y = find_head()
    # checking for each direction if it works
    possibilities = []
    # checking if there is a field to the left and that it's either empty or an apple
    if 0 < x and board[y][x - 1] <= 0:
        possibilities.append("l")
    # checking if there is a field to the right and that it's either empty or an apple
    if x + 1 < w and board[y][x + 1] <= 0:
        possibilities.append("r")
    # checking if there is a field to the top and that it's either empty or an apple
    if 0 < y and board[y - 1][x] <= 0:
        possibilities.append("u")
    # checking if there is a field to the bottom and that it's either empty or an apple
    if y + 1 < h and board[y + 1][x] <= 0:
        possibilities.append("d")

    # if it's not possible to survive go completely random. meaning everything is possible again
    if not possibilities:
        possibilities = ["l", "r", "u", "d"]

    # taking one of those possibilities
    print(choice(possibilities))




