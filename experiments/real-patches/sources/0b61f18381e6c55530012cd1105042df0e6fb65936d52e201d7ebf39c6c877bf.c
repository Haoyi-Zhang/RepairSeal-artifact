/**/
#include <stdio.h>
#include <math.h>
#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
int main(int argc, char *argv[]){
int a, b, c, median=0;
//printf("Please enter 3 numbers separated by spaces > ");
//scanf("%d%d%d", &a, &b, &c);
a = atoi(argv[1]);
b = atoi(argv[2]);
c = atoi(argv[3]);
if (((c > b) && (a < c)))
	median = a;
else if (((b > 4) && (b > 4)))
	median = b;
else if (c > a && c < b)
	median = c;
printf("%d\n", ANGELIX_OUTPUT(int, median, "stdout"));
return 0;}
