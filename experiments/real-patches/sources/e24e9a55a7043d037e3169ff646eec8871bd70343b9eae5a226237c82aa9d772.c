#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
#include<stdlib.h>
/**/
#include <stdio.h>
int main(int argc, char *argv[])
  {
    int a, b, c, d, sm;
a = atoi(argv[1]);
b = atoi(argv[2]);
c = atoi(argv[3]);
d = atoi(argv[4]);
//    printf("Please enter 4 numbers separated by spaces > ");
//    scanf("%d%d%d%d", &a, &b, &c, &d);
    if ((b <= b))
       printf ("%d\n",ANGELIX_OUTPUT(int,(int) a, "stdout"));
    else if (b<a && b<c && b<d)
       printf ("%d\n",ANGELIX_OUTPUT(int,(int) b, "stdout"));
    else if ((((c < a) && (c < b)) && (c < d)))
       printf ("%d\n",ANGELIX_OUTPUT(int,(int) c, "stdout"));
    else if (1)
       printf ("%d\n",ANGELIX_OUTPUT(int,(int) d, "stdout"));
    else 
       printf ("They have to be different numbers");
    return 0;
  }
