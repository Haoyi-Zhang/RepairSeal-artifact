#include <stdio.h>
int main(void)
{
  int num1;
  int num2;
  int num3;
  int median;
  int bigger12;
  int smaller12;
  scanf("%d%d%d", &num1, &num2, &num3);
  if (num1 < num2)
  {
    bigger12 = num2;
    smaller12 = num1;
  }
  else
  {
    bigger12 = num1;
    smaller12 = num2;
  }
  ;
  if (bigger12 < num3)
    median = bigger12;
  else
    if (num3 > smaller12)
    median = num3;
  else
    median = smaller12;
  printf("%d\n", median);
  return 0;
}

