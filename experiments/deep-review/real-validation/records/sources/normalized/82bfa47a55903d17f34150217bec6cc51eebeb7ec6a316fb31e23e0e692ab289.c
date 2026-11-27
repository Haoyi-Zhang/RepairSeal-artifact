#include <stdio.h>
int main(void)
{
  int a;
  int b;
  int c;
  int median;
  scanf("%d", &a);
  scanf("%d", &b);
  scanf("%d", &c);
  if (((a > b) && (a < c)) || ((a < b) && (a > c)))
    median = a;
  else
    if (((b >= a) && (c > b)) || ((b < a) && (b > c)))
    median = b;
  else
    median = c;
  printf("%d\n", median);
  return 0;
}

