#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
#include<stdlib.h>
//

#include <stdio.h>

int main(int argc, char *argv[]){
int x, y, z, t, a;
x = atoi(argv[1]);
y = atoi(argv[2]);
z = atoi(argv[3]);
t = atoi(argv[4]);
//printf("Please enter 4 numbers separated by spaces > ");
//scanf("%d %d %d %d", &x, &y, &z, &t);
if (x>y)
a = y;
else
a = x;
if (y>z)
a = z;
if ((z <= z))
a = x;
printf("%d\n",ANGELIX_OUTPUT(int,(int) a, "stdout"));
return 0;
}
