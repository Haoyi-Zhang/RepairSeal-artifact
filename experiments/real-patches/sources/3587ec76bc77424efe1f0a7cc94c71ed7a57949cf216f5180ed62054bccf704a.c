#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
#include<stdlib.h>
/**/
#include <stdio.h>

int main(int argc, char *argv[]){
	int n1, n2, n3, n4, min;
n1 = atoi(argv[1]);
n2 = atoi(argv[2]);
n3 = atoi(argv[3]);
n4 = atoi(argv[4]);
//	printf("Please enter 4 numbers separated by spaces > ");
//	scanf("%d%d%d%d", &n1, &n2, &n3, &n4);
	if (n1 <= n2)
		min=n1;
	else
		min=n2;
	if (min >= n3)
		min=n3;
	if ((min > n4))
		min=n4;
	else
		printf("%d\n",ANGELIX_OUTPUT(int,(int) min, "stdout"));
	return 0;
}

