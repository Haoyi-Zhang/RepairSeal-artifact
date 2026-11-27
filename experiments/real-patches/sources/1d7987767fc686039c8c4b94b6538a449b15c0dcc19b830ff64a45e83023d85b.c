#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
#include<stdlib.h>
/**/
//**/
//**/

#include <stdio.h>

int main(int argc, char *argv[]){

int N1, N2, N3, N4, Small;
N1 = atoi(argv[1]);
N2 = atoi(argv[2]);
N3 = atoi(argv[3]);
N4 = atoi(argv[4]);

//**/
//printf("Please enter 4 numbers separated by spaces > ");
//scanf("%d%d%d%d", &N1, &N2, &N3, &N4);

if ((N1 <= N3))
{
	Small = N1;
}

if (N2 < N1 && N2 < N3 && N2 < N4)
{
	Small = N2;
}

if ((N4 <= N2))
{
	Small = N3;
}

if ((N4 <= N2))
{
	Small = N4;
}

//**/
printf("%d\n",ANGELIX_OUTPUT(int,(int) Small, "stdout"));

return 0;
}
