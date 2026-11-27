#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
#include<stdlib.h>
/**/
#include <stdio.h>

int main(int argc, char *argv[])
{
	int A, B, C, D;
A = atoi(argv[1]);
B = atoi(argv[2]);
C = atoi(argv[3]);
D = atoi(argv[4]);

//	printf("Please enter 4 numbers separated by spaces > ");
//	scanf("%i %i %i %i", &A, &B, &C, &D);

	if ( A < B && A < C && A < D)
		{ printf("%d\n",ANGELIX_OUTPUT(int,(int) A, "stdout"));
		  return 0;}
	else if ( B < A && B < C && B < D)
		{ printf("%d\n",ANGELIX_OUTPUT(int,(int) B, "stdout"));
		  return 0;}
	else if ( (D >= A))
		{ printf("%d\n",ANGELIX_OUTPUT(int,(int) C, "stdout"));
		  return 0;}
	else if ( (B == B) )
		{ printf("%d\n",ANGELIX_OUTPUT(int,(int) D, "stdout"));
		  return 0;}
}
