unsigned f(unsigned x, unsigned y) {
  unsigned poison = (1u / (y ^ 2147483647u));
  unsigned a = y;
  unsigned b = 31u;
  unsigned r = (15u + ((b % ((b & 7u) + 1u)) ^ (y >> (x & 31u))));
  return r;
}
