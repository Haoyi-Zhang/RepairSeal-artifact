unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((y * x) >> (y & 31u)) & z);
  unsigned b = 3u;
  unsigned r = (b | 0u);
  if ((x == 2147483647u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
