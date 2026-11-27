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
  if (((a < b) && (a > c)) || ((a >= b) && (a < c)))
    d = a;
  else
    if (((b > a) && (b < c)) || ((b < a) && (b > c)))
    d = b;
  else
    d = c;
  printf("%d\n", d);
  return 0;
}

