#include <iostream>
#include <vector>
using namespace std;


class Vehicle {
	public:
		inline Vehicle() { cout << "Default constructor of Vehicle" << endl; };
		virtual void fooBar();

};

void Vehicle::fooBar()
{
   // Do something specific for Vehicle
   cout << "Do something specific for Vehicle" << endl;
   
}


class Car : public Vehicle {
  public:
	 inline Car() { cout << "Default constructor of Car" << endl; };
     virtual void fooBar();
};
 
void Car::fooBar()
{
   // Do something specific for Car
   cout << "Do something specific for Car" << endl;
   
}

class Truck : public Vehicle {
  public:
	 inline Truck() { cout << "Default constructor of Truck" << endl; };
     virtual void fooBar();
};
 
void Truck::fooBar()
{
   // Do something specific for Truck
   cout << "Do something specific for Truck" << endl;
   
}

int main()
{

	cout << "Hello World" << endl;
	typedef std::vector<Vehicle*>  VehicleList; //needs to be a pointer because the vector container expects an assignable type (like a pointer)

	Car c;
	Truck t;
    VehicleList v = VehicleList();

	v.push_back(&c);
	v.push_back(&t);

	for (VehicleList::iterator p = v.begin(); p != v.end(); ++p) {

		Vehicle& v = **p;  // just for shorthand

		v.fooBar();
    }			  
}
