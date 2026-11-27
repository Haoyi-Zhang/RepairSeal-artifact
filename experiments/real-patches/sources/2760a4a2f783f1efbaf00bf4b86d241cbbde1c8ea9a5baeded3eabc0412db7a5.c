#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
#include<stdlib.h>
/**/

#include <stdio.h>

int main(int argc, char *argv[]){
	double num1, num2, num3, num4;
 num1 = strtod(argv[1], NULL);num2 = strtod(argv[2], NULL);num3 = strtod(argv[3], NULL);num4 = strtod(argv[4], NULL);//	printf("Please enter 4 numbers separated by spaces > ");
//	scanf("%lf%lf%lf%lf",&num1,&num2,&num3,&num4);
	if ((num1 <= num1))
	printf("%d\n",ANGELIX_OUTPUT(int,(int)num1, "stdout"));
	if ((num1 < num1))
	printf("%d\n",ANGELIX_OUTPUT(int,(int)num2, "stdout"));
	if (num3<num1 && num3<num2 && num3<num4)
	printf("%d\n",ANGELIX_OUTPUT(int,(int)num3, "stdout"));
	if (num4<num1 && num4<num2 && num4<num4)
	printf("%d\n",ANGELIX_OUTPUT(int,(int)num4, "stdout"));
	return 0; 
}
