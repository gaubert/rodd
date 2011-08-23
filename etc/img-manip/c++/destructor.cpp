#include <iostream>
using namespace std;

class Bar {
	public:
	  Bar();
	  ~Bar();
};

Bar::Bar()
{
  cout << "In Bar Default Constructor" << endl;
}

Bar::~Bar()
{
  cout << "In Bar Destructor" << endl;
}

class Foo {
  private:
    char _c;
	Bar b1_;
	Bar b2_;
  public:
	Foo();
	~Foo();
	Foo(const Foo& copy);
    Foo(char x);
	inline char c() { return _c; };
	Foo return_a_foo();
    void passed_by_value(Foo aFoo);
};

Foo::Foo()
{
  cout << "Default constructor called." << endl;
}

Foo::Foo(const Foo& copy):_c(copy._c)
{
  cout << "In copy constructor" << endl;
}

 
Foo::Foo(char x): _c(x)
{
  cout << "Char constructor called" << endl;
}	    

Foo::~Foo()
{
  cout << "In Destructor" << endl;
}


Foo Foo::return_a_foo()
{
  Foo foo('z');
  return foo; //return by value. Copy constructor should be called
}

void Foo::passed_by_value(Foo aFoo)
{
  char c = aFoo.c();
}

int main()
{
  cout << "In Main" << endl;
  cout << "Create object in a block. Destructor called when block is left" << endl;
  {
    Foo foo;
  }
}
