#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
#include<stdlib.h>
/**/

#include <stdio.h>
#include <math.h>

int main (int argc, char *argv[]) {

  int num1, num2, num3, num4;
num1 = atoi(argv[1]);
num2 = atoi(argv[2]);
num3 = atoi(argv[3]);
num4 = atoi(argv[4]);

//  printf("Please enter 4 numbers separated by spaces > ");
//  scanf("%d%d%d%d", &num1, &num2, &num3, &num4);

  if(num1 < num2 && num1 < num3 && num1 < num4)
    {
      printf("%d\n",ANGELIX_OUTPUT(int,(int) num1, "stdout"));
    }
  else if(num2 < num1 && num2 < num3 && num2 < num4)
    {
      printf("%d\n",ANGELIX_OUTPUT(int,(int) num2, "stdout"));
	     }
      else if((((num3 < num1) && (num3 < num2)) && (num3 < num4)))
	{
	  printf("%d\n",ANGELIX_OUTPUT(int,(int) num3, "stdout"));
	}
      else if((num4 <= num1))
	{
	  printf("%d\n",ANGELIX_OUTPUT(int,(int) num4, "stdout"));
	}

      return 0;
    }
