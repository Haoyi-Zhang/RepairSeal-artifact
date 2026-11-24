unsigned f(unsigned x, unsigned y) {
  unsigned a = ((~(x / ((x & 7u) + 1u))) % (((3u + x) & 7u) + 1u));
  unsigned b = x;
  unsigned r = ((x ^ (b % ((y & 7u) + 1u))) % ((2u & 7u) + 1u));
  return r;
}
