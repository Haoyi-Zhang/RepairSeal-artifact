unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (z - (y >> ((3u / ((x & 7u) + 1u)) & 31u)));
  unsigned b = a;
  unsigned r = y;
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
