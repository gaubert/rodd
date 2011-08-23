#include <iostream>
using namespace std;

class Shape {
 public:
    virtual Shape* clone() const = 0;  // = 0 means it is "pure virtual"
}; 

class Circle : public Shape {
 public:
   virtual Circle* clone() const;
};
		    
Circle* Circle::clone() const
{
   return new Circle(*this);
} 

class Fred {
 public:
   // p must be a pointer returned by new; it must not be NULL
   Fred(Shape* p)
     : p_(p) { assert(p != 0); }
   ~Fred()
     { delete p_; }
   Fred(Fred const& f)
     : p_(f.p_->clone()) { }
   Fred& operator= (Fred const& f)
     {
       if (this != &f) {              // Check for self-assignment
         Shape* p2 = f.p_->clone();   // Create the new one FIRST...
         delete p_;                   // ...THEN delete the old one
         p_ = p2;
       }
       return *this;
     }

 private:
   Shape* p_;
 }; 

int main()
{

}
