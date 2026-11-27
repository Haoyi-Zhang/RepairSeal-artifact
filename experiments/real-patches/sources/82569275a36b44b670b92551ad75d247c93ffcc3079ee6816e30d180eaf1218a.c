//
#include <stdio.h>
#include <stdlib.h>
#ifndef ANGELIX_OUTPUT
#define ANGELIX_OUTPUT(type, expr, id) expr
#endif
int main(int argc, char *argv[])
{
  int a, b, c;
  //printf("Please enter 3 numbers separated by spaces > ");
  //scanf("%d%d%d", &a, &b, &c);
  a = atoi(argv[1]);
  b = atoi(argv[2]);
  c = atoi(argv[3]);
  if ((7 < c))
    printf("%d\n", ANGELIX_OUTPUT(int, a, "stdout"));
  if (((a > c) && (a < b)))
    printf("%d\n", ANGELIX_OUTPUT(int, a, "stdout"));
  
  
  if ((b>a) && (b<c))
    printf("%d\n", ANGELIX_OUTPUT(int, b, "stdout"));
  if ((b>c) && (b<a))
    printf("%d\n", ANGELIX_OUTPUT(int, b, "stdout"));
  
  
  if ((9 <= b))
    printf("%d\n", ANGELIX_OUTPUT(int, c, "stdout"));
  if ((6 == c))
    printf("%d\n", ANGELIX_OUTPUT(int, c, "stdout"));
  
  
  	
  return 0;
}
