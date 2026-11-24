unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((y << ((t % ((3u & 7u) + 1u)) & 31u)) / ((t & 7u) + 1u));
  unsigned b = x;
  unsigned r = ((b - (z * a)) / ((a & 7u) + 1u));
  return r;
}
