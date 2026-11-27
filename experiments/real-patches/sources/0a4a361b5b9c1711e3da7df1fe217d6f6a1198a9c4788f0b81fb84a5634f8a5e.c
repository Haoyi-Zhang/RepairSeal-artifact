/**/

#include <stdio.h>
#include <math.h>
#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
int main (int argc, char *argv[]) {

int a;
int b;
int c;

//printf("Please enter 3 numbers seperated by spaces > ");
//scanf("%d %d %d", &a, &b, &c);
a = atoi(argv[1]);
b = atoi(argv[2]);
c = atoi(argv[3]);
if( (b > b))
printf("%d\n", ANGELIX_OUTPUT(int, b, "stdout"));
if( (b <= a))
printf("%d\n", ANGELIX_OUTPUT(int, a, "stdout"));
if((a<c && c<b) || (b<c && c<a))
printf("%d\n", ANGELIX_OUTPUT(int, c, "stdout"));

return 0;

}
