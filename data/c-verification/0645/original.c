unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (t ^ ((x ^ 31u) - (t ^ x)));
  unsigned b = (t << ((~(2147483647u >> (a & 31u))) & 31u));
  unsigned r = (((x & x) & (t << (a & 31u))) + ((b / ((a & 7u) + 1u)) >> ((t / ((x & 7u) + 1u)) & 31u)));
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
