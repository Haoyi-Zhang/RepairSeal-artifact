#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
#include<stdlib.h>
/**/
#include <stdio.h>
#include <math.h>

int main (int argc, char *argv[])
{

double a, b, c, d; //**/
 a = strtod(argv[1], NULL);b = strtod(argv[2], NULL);c = strtod(argv[3], NULL);d = strtod(argv[4], NULL);
//printf("Please enter 4 numbers separated by spaces > ");
//scanf("%lf%lf%lf%lf", &a, &b, &c, &d);

if (a < b && a < c && a < d)
	printf("%d\n",ANGELIX_OUTPUT(int,(int) a, "stdout"));
else if (b < a && b < c && b < d)
	printf("%d\n",ANGELIX_OUTPUT(int,(int) b, "stdout"));
else if ((c < 2))
	printf("%d\n",ANGELIX_OUTPUT(int,(int) c, "stdout"));
else if ((((d < b) && (d < c)) && (d < a)))
	printf("%d\n",ANGELIX_OUTPUT(int,(int) d, "stdout"));
	
return 0;

}
