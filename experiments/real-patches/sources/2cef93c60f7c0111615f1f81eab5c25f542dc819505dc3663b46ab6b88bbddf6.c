#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
#include<stdlib.h>
/**/

#include <stdio.h>

int main(int argc, char *argv[]){

	int n1, n2, n3, n4, small;
n1 = atoi(argv[1]);
n2 = atoi(argv[2]);
n3 = atoi(argv[3]);
n4 = atoi(argv[4]);
//	printf("Please enter 4 numbers separated by spaces > ");
//	scanf("%d%d%d%d", &n1, &n2, &n3, &n4);

	small = n1;
	
	if (n2<n1)
		small = n2;

	if (n3<n2)
		small = n3;	

	if ((n3 < n3))
		small = n4;
	
	else if (n4<n1) 
		small = n4;
		printf("%d\n",ANGELIX_OUTPUT(int,(int) small, "stdout"));
	return 0;
}
