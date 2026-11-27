#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
#include<stdlib.h>
/**/

#include <stdio.h>
#include <math.h>

int
main(int argc, char *argv[])
{
	int first, second, third, fourth;
first = atoi(argv[1]);
second = atoi(argv[2]);
third = atoi(argv[3]);
fourth = atoi(argv[4]);
//	printf("Please enter 4 numbers separated by spaces > ");
//	scanf("%i", &first);
//	scanf("%i", &second);
//	scanf("%i", &third);
//	scanf("%i", &fourth);

	if ((first < fourth))
		printf("%d\n",ANGELIX_OUTPUT(int,(int) first, "stdout"));
	if ((((second < first) && (second < third)) && (second < fourth)))
		printf("%d\n",ANGELIX_OUTPUT(int,(int) second, "stdout"));
	if ((third<first) && (third<second) && (third<fourth))
		printf("%d\n",ANGELIX_OUTPUT(int,(int) third, "stdout"));
	if ((fourth<third) && (fourth<second) && (fourth<first))
		printf("%d\n",ANGELIX_OUTPUT(int,(int) fourth, "stdout"));

	return(0);
}
