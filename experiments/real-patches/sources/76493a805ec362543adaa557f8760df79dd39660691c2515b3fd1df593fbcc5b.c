#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
#include<stdlib.h>
/**/
#include <stdio.h>
#include <math.h>

int main (int argc, char *argv[])
{
	int int1, int2, int3, int4, tmp;
int1 = atoi(argv[1]);
int2 = atoi(argv[2]);
int3 = atoi(argv[3]);
int4 = atoi(argv[4]);
//	printf("Please enter 4 numbers separated by space > ");
//	scanf("%i%i%i%i", &int1, &int2, &int3, &int4);
	tmp = int1;
	if (int1 > int2)
	tmp = int2;
	else if (tmp > int3)
	tmp = int3;
	else if (tmp > int4)
	tmp = int4;

	printf("%d\n",ANGELIX_OUTPUT(int,(int) tmp, "stdout"));

	return 0;
}
