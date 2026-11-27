#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
#include<stdlib.h>
/**/
//**/

#include <stdio.h>

int main(int argc, char *argv[]) {

double a, b, c, d, m, n, p;
 a = strtod(argv[1], NULL);b = strtod(argv[2], NULL);c = strtod(argv[3], NULL);d = strtod(argv[4], NULL);
//printf("Please enter 4 numbers separated by spaces > ");
//scanf("%lf""%lf""%lf""%lf", &a, &b, &c, &d);

if (a > b)
m=b;
else if (a < b)
m=a;

if (m > c)
n=c;
else if (m < c)
n=m;

if (n > d)
p=d;
else if (n < d)
p=n;

printf("%d\n",ANGELIX_OUTPUT(int,(int) p, "stdout"));

return(0);

}
