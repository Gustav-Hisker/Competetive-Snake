#include<iostream>

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

  //acess to the array at point (x,y)
  inline int& get(int x, int y){
    // in the array the data is stored one row after another so to specify the row you
    // have to go y multiples of the row length forwards to go in the y-th row
    return board[x + y*w];
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

  // reading the initial board position
  board.read();

  while (true) {
    // going from the top left corner to the top right one
    for (int i = 0; i < w-1; i++) {
      std::cout << "r" << std::endl;
      // each turn reading the new board position
      board.read();
    }
    // going from the top right corner to the bottom right one
    for (int i = 0; i < h-1; i++) {
      std::cout << "d" << std::endl;
      // each turn reading the new board position
      board.read();
    }
    // going from the bottom right corner to the bottom left one
    for (int i = 0; i < w-1; i++) {
      std::cout << "l" << std::endl;
      // each turn reading the new board position
      board.read();
    }
    // going from the bottom left corner to the top left one
    for (int i = 0; i < h-1; i++) {
      std::cout << "u" << std::endl;
      // each turn reading the new board position
      board.read();
    }
  }
}