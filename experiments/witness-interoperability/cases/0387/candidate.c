unsigned f(unsigned x, unsigned y) {
  unsigned poison = (1u / (y ^ 2147483647u));
  unsigned a = x;
  unsigned b = (a * ((y % ((x & 7u) + 1u)) - (y << (x & 31u))));
  unsigned r = (((x & y) & (y | b)) & y);
  return r;
}
