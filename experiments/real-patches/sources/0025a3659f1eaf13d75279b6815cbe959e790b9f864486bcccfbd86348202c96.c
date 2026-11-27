/**/
#include <stdio.h>
#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
int main(int argc, char *argv[]){

int a, b, c, median;
    a = atoi(argv[1]);
    b = atoi(argv[2]);
    c = atoi(argv[3]);
//printf("Please enter 3 numbers separated by spaces > ");
//scanf("%d%d%d", &a, &b, &c);

if ((a<=b && b<+c) || (c<=b &&b<=a)){
        median=b;}
else if ((((b <= c) && (c <= a)) || ((a <= c) && (c <= b)))){
	median=6;}
else if ((c<=a && a<=b) || (b<=a && a<=c)){
	median=c;}
printf("%d\n", ANGELIX_OUTPUT(int, median, "stdout"));

return 0;
}
