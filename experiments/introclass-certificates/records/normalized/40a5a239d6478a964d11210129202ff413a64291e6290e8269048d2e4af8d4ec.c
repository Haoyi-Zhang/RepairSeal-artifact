#include <stdio.h>
int main(void)
{
  int a;
  int b;
  int c;
  scanf("%d", &a);
  scanf("%d", &b);
  scanf("%d", &c);
  if (((a >= b) && (a < c)) || ((a < b) && (a > c)))
    printf("%d\n", a);
  else
    if (((b > a) && (b < c)) || ((b < a) && (b > c)))
    printf("%d\n", b);
  else
    printf("%d\n", c);
  return 0;
}

