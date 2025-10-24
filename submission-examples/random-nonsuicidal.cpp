#include<iostream>
#include <algorithm> // for the random shuffle
#include <vector>

// helper class accessing an array which contains the data of the board
class Board{
  int w;
  int h;
  int* board;

  public:
  Board(int width, int height){
    w = width;
    h = height;
    board = new int[w*h];
  }

  // access to the array at point (x,y)
  inline int& get(int x, int y){
    // in the array the data is stored one row after another so to specify the row you
    // have to go y multiples of the row length forwards to go in the y-th row
    return board[x + y*w];
  }

  // function to get the coordinates of the head of the snake this program controls
  void findHead(int& x, int& y){
    // iterating over all fields on the board
    for (int i = 0; i < w; i++) {
      for (int j = 0; j < h; j++) {
        // saving the the cords if the head was found
        if (get(i,j) == 1){
          x = i;
          y = j;
          return;
        }
      }
    }
  }

  // method to read the input
  void read(){
    // iterating over the w*h entries and saving them in the array
    for (int i = 0; i < w*h; i++) {
      std::cin >> board[i];
    }
  }
};


int main(){
  // reading the width and the height
  int w, h;
  std::cin >> w >> h;

  // declaring the board variable which saves the information of the current game state
  Board board(w, h);

  // repeating forever (until the program gets terminated)
  while (true) {
    // reading the current state of the board
    board.read();

    // getting heads position
    int x, y;
    board.findHead(x, y);

    // checking for each direction if it works
    std::vector<char> possibilities(0);
    // checking if there is a field to the left and that it's either empty or an apple
    if (0 < x && board.get(x - 1,y) <= 0)
        possibilities.push_back('l');
    // checking if there is a field to the right and that it's either empty or an apple
    if (x + 1 < w && board.get(x + 1,y) <= 0)
        possibilities.push_back('r');
    // checking if there is a field to the top and that it's either empty or an apple
    if (0 < y && board.get(x,y -1) <= 0)
        possibilities.push_back('u');
    // checking if there is a field to the bottom and that it's either empty or an apple
    if (y + 1 < h and board.get(x,y + 1) <= 0)
        possibilities.push_back('d');

    // if it's not possible to survive go completely random. meaning everything is possible again
    if (0 == possibilities.size())
        possibilities = {'l', 'r', 'u', 'd'};

    // taking one of those possibilities
    std::cout << possibilities[std::rand()%std::ssize(possibilities)] << std::endl;
  }
}