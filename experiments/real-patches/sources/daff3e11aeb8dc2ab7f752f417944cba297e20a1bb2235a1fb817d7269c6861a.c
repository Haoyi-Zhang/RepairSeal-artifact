/**/

#include<stdio.h>
#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif

int
main(int argc, char *argv[])
{

int x,y, z;

//**/
//printf("Please enter 3 numbers separated by space  > ");
//scanf("%d%d%d",&x,&y,&z);
x = atoi(argv[1]);
y = atoi(argv[2]);
z = atoi(argv[3]);
if (x>=y && x<=z)
printf("%d\n", ANGELIX_OUTPUT(int, x, "stdout"));

else if (y>=x && y<=z)
printf("%d\n", ANGELIX_OUTPUT(int, y, "stdout"));

else
printf("%d\n", ANGELIX_OUTPUT(int, z, "stdout"));

return(0);
}
