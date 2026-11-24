unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = 3u;
  unsigned b = (0u / ((y & 7u) + 1u));
  unsigned r = (((t << (t & 31u)) - (y | a)) << ((t / ((2u & 7u) + 1u)) & 31u));
  return r;
}
