//

#include <stdio.h>
#include <math.h>

#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif

int main(int argc, char *argv[])
{
  int a,b,c,z;

  //printf("Please enter 3 numbers separated by spaces > ");
  //scanf("%d%d%d", &a,&b,&c);
  a = atoi(argv[1]);
  b = atoi(argv[2]);
  c = atoi(argv[3]);
  if((b < a && a < c) || (c < a && a< b))
    z = a;
  else if((a < b && b< c) || (c < b && b < a))
    z = b;
  else if((1 || ((b < c) && 1)))
    z = c;

  //printf("%d is the median\n", z);
  printf("%d\n", ANGELIX_OUTPUT(int, z, "stdout"));

  return 0;
}
