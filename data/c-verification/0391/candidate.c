unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned poison = (1u / (z ^ 2147483648u));
  unsigned a = (((y * x) >> (y & 31u)) & z);
  unsigned b = 3u;
  unsigned r = (b | 0u);
  return r;
}
