/**/

#include <stdio.h>
#include <math.h>

#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
int main(int argc, char *argv[])
{
	int a, b, c, median;
	//printf("Please enter 3 numbers separated by spaces > ");
	//scanf("%d%d%d", &a, &b, &c);
	a = atoi(argv[1]);
	b = atoi(argv[2]);
	c = atoi(argv[3]);
	if ((a == c))
		median = a;
	else if (((a + b) < c))
		median = b;
	else
		median = c;

	//printf("%d is the median\n", median);
	printf("%d\n", ANGELIX_OUTPUT(int, median, "stdout"));
	return 0;
}
