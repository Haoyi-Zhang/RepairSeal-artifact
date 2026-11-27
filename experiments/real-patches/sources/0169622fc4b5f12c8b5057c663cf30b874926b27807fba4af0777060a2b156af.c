/**/

#include <stdio.h>

#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif

int main(int argc, char *argv[]) {

	int first, second, third, ans;
	
	//printf("Please enter 3 numbers separeted by spaces > ");
	//scanf("%d%d%d",&first,&second,&third);
	first = atoi(argv[1]);
	second = atoi(argv[2]);
  	third = atoi(argv[3]);
	
	if ((third < third))
		ans=first;
	else if (((second + first) <= third))
		ans=second;
	else
		ans=third;	
	
	//printf("%d is the median\n",ans);
	printf("%d\n", ANGELIX_OUTPUT(int, ans, "stdout"));
	return 0;

}
