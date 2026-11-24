unsigned f(unsigned x, unsigned y) {
  unsigned a = (x % ((0u & 7u) + 1u));
  unsigned b = (((a / ((y & 7u) + 1u)) / ((31u & 7u) + 1u)) & (y | (y >> (31u & 31u))));
  unsigned r = a;
  return r;
}
