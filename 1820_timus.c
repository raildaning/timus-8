#include <stdio.h>

short int timeToFire(short int n, short int k) {
  short int time_to_one = (n * 2);
  short int rest = time_to_one % k;
  short int result = time_to_one / k;
  if (k >= n)
    return 2;
  return (rest) ? result + 1 : result;
}

int main(void) {
  short int n, k;

  scanf("%4hd%4hd", &n, &k);
  printf("%hd\n", timeToFire(n, k));
  return 0;
}
