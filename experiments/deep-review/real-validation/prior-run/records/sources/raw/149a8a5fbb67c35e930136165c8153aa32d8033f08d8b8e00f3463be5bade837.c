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
	
	if ((((first > second) && (first < third)) || ((first > third) && (first < second))))
		ans=first;
	else if ((((third > first) && (second < third)) || ((second > third) && (second < first))))
		ans=second;
	else
		ans=third;	
	
	//printf("%d is the median\n",ans);
	printf("%d\n", ANGELIX_OUTPUT(int, ans, "stdout"));
	return 0;

}
