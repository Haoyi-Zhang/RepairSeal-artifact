unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = 2147483647u;
  unsigned b = (((2147483647u << (y & 31u)) - x) * (z + (y / ((t & 7u) + 1u))));
  unsigned r = b;
  return r;
}
