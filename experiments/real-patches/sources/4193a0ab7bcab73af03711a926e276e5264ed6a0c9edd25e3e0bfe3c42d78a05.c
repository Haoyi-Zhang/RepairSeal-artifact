/**/
#include <stdio.h>
#include <math.h>
#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
int main(int argc, char *argv[]){

int num1,num2,num3,median;

//printf("Please enter 3 numbers separated by spaces > ");
//scanf("%d%d%d",&num1,&num2,&num3);
num1 = atoi(argv[1]);
num2 = atoi(argv[2]);
num3 = atoi(argv[3]);
if((num2 == num1)) 
median=num1;
else if ((3 <= num3))
median=num2;
else
median=num3;

printf("%d\n", ANGELIX_OUTPUT(int, median, "stdout"));
return(0);
}
