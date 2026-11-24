unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (~((t | z) >> ((x | y) & 31u)));
  unsigned b = (((x + 3u) % ((t & 7u) + 1u)) + (y / ((y & 7u) + 1u)));
  unsigned r = (2147483647u >> (((t & x) - (x & a)) & 31u));
  return r;
}
