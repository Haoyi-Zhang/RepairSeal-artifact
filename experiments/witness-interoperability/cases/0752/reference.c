unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (y % (((3u ^ (1u / ((y & 7u) + 1u))) & 7u) + 1u));
  unsigned b = 0u;
  unsigned r = ((x & (a ^ b)) >> ((31u - 3u) & 31u));
  return r;
}
