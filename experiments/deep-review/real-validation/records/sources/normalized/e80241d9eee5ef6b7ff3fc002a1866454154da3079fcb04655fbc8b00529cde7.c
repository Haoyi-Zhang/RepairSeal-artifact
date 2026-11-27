#include <stdio.h>
int main(void)
{
  int num1;
  int num2;
  int num3;
  int num4;
  int bigger;
  int bigger2;
  int biggest;
  scanf("%d%d%d%d", &num1, &num2, &num3, &num4);
  if (num1 < num2)
    bigger = num1;
  else
    bigger = num2;
  if (num4 < num3)
    bigger2 = num4;
  else
    bigger2 = num3;
  if (bigger < bigger2)
    biggest = bigger;
  else
    biggest = bigger2;
  printf("%d\n", biggest);
  return 0;
}

