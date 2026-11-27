/**/

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
int
main(int argc, char *argv[])
{
	double first, second, third;
	first = strtod(argv[1], NULL);
        second = strtod(argv[2], NULL);
        third = strtod(argv[3], NULL);
	//printf("Please enter 3 numbers seperated by spaces > ");
	//scanf("%lf", &first);
	//scanf("%lf", &second);
	//scanf("%lf", &third);

	if ((((first > second) && (first < third)) || ((first < second) && (first > third))))
		printf("%d\n", ANGELIX_OUTPUT(int, (int)first, "stdout"));
	if ((((second > first) && (second < third)) || 1))
		printf("%d\n", ANGELIX_OUTPUT(int, (int)second, "stdout"));
	if ((third>first && third<second) || (third<first && third>second))
		printf("%d\n", ANGELIX_OUTPUT(int, (int)third, "stdout"));
	return(0);
}
