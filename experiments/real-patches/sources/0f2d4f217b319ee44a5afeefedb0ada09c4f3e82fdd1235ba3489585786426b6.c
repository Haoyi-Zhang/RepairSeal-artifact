#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
#include<stdlib.h>
//
//
//


#include <stdio.h>
#include <math.h>

int main(int argc, char *argv[]) {
int a, b, c, d; //
a = atoi(argv[1]);
b = atoi(argv[2]);
c = atoi(argv[3]);
d = atoi(argv[4]);


//
//printf("Please enter 4 numbers seperated by spaces > ");
//scanf("%d%d%d%d", &a, &b, &c, &d);

//

//
if ((a<b)&&(a<c)&&(a<d))
{
	printf("%d\n",ANGELIX_OUTPUT(int,(int) a, "stdout"));
}
//
else if ((b<a)&&(b<c)&&(b<d))
{	
	printf("%d\n",ANGELIX_OUTPUT(int,(int) b, "stdout"));
}
//
else if (((c <= b) && (c < d)))
{
	printf("%d\n",ANGELIX_OUTPUT(int,(int) c, "stdout"));
}
//
else if ((((d < a) && (d < b)) && (d < c)))
{
	printf("%d\n",ANGELIX_OUTPUT(int,(int) d, "stdout"));

}
return(0);
}
