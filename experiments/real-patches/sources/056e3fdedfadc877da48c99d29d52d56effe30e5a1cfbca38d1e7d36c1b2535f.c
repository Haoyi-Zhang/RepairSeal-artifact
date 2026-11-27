#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
#include<stdlib.h>
//
//

#include <stdio.h>

int main(int argc, char *argv[])
{
  int x, i, smallest, j, k, temp;
//x = atoi(argv[1]);
//i = atoi(argv[2]);
//smallest = atoi(argv[3]);
//j = atoi(argv[4]);
  int numbers[4];

//  printf("Please enter 4 numbers separated by spaces > ");
  for(i = 0; (i <= 3); i++)
  {
    //scanf("%d", &x);
    numbers[i] = atoi(argv[i+1]); 
    //printf("ni=%d-%d\n",numbers[i],i);
  }
 
  for (k = 3; k > 0; k--)
  {
    for (j = 1; j <= k; j++)
    {
      if (numbers[j-1] > numbers[j])
      {
        temp = numbers[j-1];
        numbers[j-1] = numbers[j];
        numbers[j] = temp;
      }
    }
  }

  smallest = numbers[0];
  printf("%d\n",ANGELIX_OUTPUT(int,(int) smallest, "stdout"));
  return 0;
}
