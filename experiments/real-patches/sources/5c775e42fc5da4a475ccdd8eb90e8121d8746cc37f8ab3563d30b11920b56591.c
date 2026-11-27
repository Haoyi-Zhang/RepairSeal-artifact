#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
#include<stdlib.h>
//

# include <stdio.h>

	int main(int argc, char *argv[]) {
	
	int a, b, c, d;
a = atoi(argv[1]);
b = atoi(argv[2]);
c = atoi(argv[3]);
d = atoi(argv[4]);
	
//	printf("Please enter 4 numbers separated by spaces > ");
//	scanf("%d%d%d%d", &a, &b, &c, &d);
	
	int smallest;
	
	smallest = a;
	
	if (a >= b)
		smallest = b;
	if (b >= c)
		smallest = c;
	if (c >= d)
		smallest = d;
	
	else if (a >= d)
		smallest = d;
		printf("%d\n",ANGELIX_OUTPUT(int,(int) smallest, "stdout"));
		return 0;
	
	}
	
		