#include <stdio.h>
int main(void)
{
  int first;
  int second;
  int third;
  int ans;
  scanf("%d", &first);
  scanf("%d", &second);
  scanf("%d", &third);
  if (((first > second) && (first < third)) || ((first > third) && (first < second)))
    ans = first;
  else
    if (((second > first) && (second < third)) || ((second > third) && (second < first)))
    ans = second;
  else
    ans = third;
  printf("%d\n", ans);
  return 0;
}

