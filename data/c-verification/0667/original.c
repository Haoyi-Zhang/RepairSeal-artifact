unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = (a + ((a << (31u & 31u)) / (((0u / ((3u & 7u) + 1u)) & 7u) + 1u)));
  unsigned r = (y * x);
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
