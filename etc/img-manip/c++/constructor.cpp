#include <iostream>
using namespace std;

class Foo {
  private:
    char _c;
  public:
	Foo();
    Foo(char x);
    Foo(char x, int y);
	inline char c() { return _c; };
};

Foo::Foo()
{
  cout << "Default constructor called." << endl;
}

 
Foo::Foo(char x): _c(x)
{
  cout << "Char constructor called" << endl;
}	    

int main()
{
  cout << "In Main" << endl;
  cout << "Call default constructor" << endl;
  Foo foo;
  cout << "Call f('c')" << endl;
  Foo f('c');
  cout << "Foo precious = " << f.c() << endl;
}
