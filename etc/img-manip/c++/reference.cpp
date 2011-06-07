#include <iostream>
using namespace std;

void swap(int& i, int& j)
{
   int tmp = i;
   i = j;
   j = tmp;
}

void assign(int& i, int val)
{
	i = val;
}
 
int main()
{
  int x, y;
  x = 1;
  y = 10;
  cout << "Hello World" << endl;
  cout << "x =" << x << ", y =" << y << endl;

  swap(x,y);

  cout << "After Swap, x =" << x << ", y =" << y << endl;

  assign(x,1000);

  cout << "After assign, x =" << x << endl;
}
