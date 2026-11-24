unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((~(x >> (y & 31u))) << ((3u << (31u & 31u)) & 31u));
  unsigned b = (((x + z) + (z * y)) % ((((3u ^ a) ^ (a / ((a & 7u) + 1u))) & 7u) + 1u));
  unsigned r = a;
  return r;
}
