
void swap(int& i, int& j)
{
   int tmp = i;
   i = j;
   j = tmp;
}
 
int main()
{
  int x, y;
  swap(x,y);
}
