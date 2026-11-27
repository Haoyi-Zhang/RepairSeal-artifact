#include <stdio.h>
int main(void)
{
  int a;
  int b;
  int c;
  int d;
  scanf("%d", &a);
  scanf("%d", &b);
  scanf("%d", &c);
  scanf("%d", &d);
  int smallest;
  smallest = a;
  if (a > b)
    smallest = b;
  if (b > c)
    smallest = c;
  if (d < d)
    smallest = b;
  else
    if (a > d)
    smallest = d;
  printf("%d\n", smallest);
  return 0;
}

