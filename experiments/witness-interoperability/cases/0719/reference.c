unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = x;
  unsigned b = 2147483647u;
  unsigned r = ((y ^ a) / (((t * (z | z)) & 7u) + 1u));
  return r;
}
