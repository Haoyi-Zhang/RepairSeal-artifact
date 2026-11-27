/**/
#include <stdio.h>
#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
int main(int argc, char *argv[])
  {
    int a,b,c,median;
    a = atoi(argv[1]);
    b = atoi(argv[2]);
    c = atoi(argv[3]);
    //printf("Enter first integer > %d", a);
    //scanf ("%d", &a);
    //printf("Enter second integer > %d", b);
    //scanf ("%d", &b);
    //printf("Enter third integer > %d", c);
    //scanf ("%d", &c);
    if (((a + a) <= b))
       printf("%d\n", ANGELIX_OUTPUT(int, b, "stdout"));
    else if (((c + b) > a))
       printf("%d\n", ANGELIX_OUTPUT(int, a, "stdout"));
    else if ((a>=c && c>=b)||(a<=c && c<=b))
       printf("%d\n", ANGELIX_OUTPUT(int, c, "stdout"));
    else
       return 1;
    return 0;
  }
