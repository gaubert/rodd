#include <iostream>
using namespace std;

class Foo {
  private:
    char _c;
  public:
	Foo();
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
  cout << "Call default constructor" << endl;
  Foo foo;
  cout << "Call f('c')" << endl;
  Foo f('c');
  cout << "Foo precious = " << f.c() << endl;
  cout << "Instanciate array of Foo 3 times" << endl;
  Foo a[3];          
  cout << "Instanciate array of Foo 3 times via pointer and new" << endl;
  Foo* p = new Foo[3];
  cout << "Use of copy constructor " << endl;
  Foo fool(f);
  cout << "fool.c() = " << fool.c() << " Should be c." << endl;

  cout << "Use of copy constructor with assignement operator" << endl;
  Foo foolish = fool;

  cout << "Return a foo by value. Copy constructor should be called" << endl;
  Foo f1 = f.return_a_foo();
  Foo another_fool(f);
  cout << "another_fool.c() = " << another_fool.c() << endl;

  cout << "Pass a foo by value. Copy constructor should be called" << endl;
  f1.passed_by_value(f);
}
