/**/

#include <stdio.h>
#include <math.h>
#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
int main (int argc, char *argv[]) {

	int a,b,c,d;
	//printf("Please enter 3 numbers separated by spaces > ");
	//scanf("%d%d%d",&a, &b, &c);
	a = atoi(argv[1]);
  	b = atoi(argv[2]);
  	c = atoi(argv[3]);
	if (1)
		d=b;
	if ((c<a && a<b) || (b<a && a<c))
		d=a;
	if ((((b < c) && (c < a)) || 1))
		d=c;

	printf("%d\n", ANGELIX_OUTPUT(int, d, "stdout"));

	return 0;
}
