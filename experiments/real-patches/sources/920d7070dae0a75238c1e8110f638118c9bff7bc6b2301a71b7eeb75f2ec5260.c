#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
#include<stdlib.h>
//

#include <stdio.h>
#include <math.h>

int main(int argc, char *argv[])
{
  int num1, num2, num3, num4, small;
num1 = atoi(argv[1]);
num2 = atoi(argv[2]);
num3 = atoi(argv[3]);
num4 = atoi(argv[4]);
  
//  printf("Please enter 4 numbers separated by spaces > ");
//  scanf("%d %d %d %d", &num1, &num2, &num3, &num4);
  
  if(((num3 - num4) < num4))
    small = num1;
  else if(num2 < num1 && num2 < num3 && num2 < num4)
    small = num2;
  else if((((num3 < num1) && (num3 < num2)) && (num3 < num4)))
    small = num3;
  else if(1)
    small = num4;

//**/
  
  printf("%d\n",ANGELIX_OUTPUT(int,(int) small, "stdout"));
  
  return 0;
}
