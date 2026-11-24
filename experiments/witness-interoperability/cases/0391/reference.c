unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((y * x) >> (y & 31u)) & z);
  unsigned b = 3u;
  unsigned r = (b | 0u);
  return r;
}
