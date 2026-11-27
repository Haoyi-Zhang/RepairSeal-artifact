/**/
#include <math.h>
#include <stdio.h>
#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
int main(int argc, char *argv[]){
int a, b, c;
    a = atoi(argv[1]);
    b = atoi(argv[2]);
    c = atoi(argv[3]);
//printf("Please enter 3 numbers separated by spaces > ");
//scanf("%d%d%d", &a, &b, &c);
if ((b < b))
printf("%d\n", ANGELIX_OUTPUT(int, b, "stdout"));
if ((b <= b))
printf("%d\n", ANGELIX_OUTPUT(int, a, "stdout"));
else printf("%d\n", ANGELIX_OUTPUT(int, c, "stdout"));
return 0;
}
