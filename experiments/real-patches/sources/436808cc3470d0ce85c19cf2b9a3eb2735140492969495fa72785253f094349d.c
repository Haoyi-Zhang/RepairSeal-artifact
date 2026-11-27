#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
#include<stdlib.h>
//
#include <stdio.h>
#include <math.h>

int main(int argc, char *argv[]) {
  int a, b, c, d, e;
a = atoi(argv[1]);
b = atoi(argv[2]);
c = atoi(argv[3]);
d = atoi(argv[4]);
//  printf ("Please enter 4 numbers separated by spaces > ");
//  scanf ("%d %d %d %d",&a,&b,&c,&d);
  if ((a < d))
    e=a;
  else if (b<a && b<c && b<d)
    e=b;
  else if ((((c < a) && (c < b)) || (c < d)))
    e=c;
  else
    e=d;
  printf("%d\n",ANGELIX_OUTPUT(int,(int) e, "stdout"));
  return 0;
}
