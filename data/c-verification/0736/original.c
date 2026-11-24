unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((x & (2147483647u & 15u)) ^ 2u);
  unsigned b = (((z ^ y) * 3u) - ((15u & z) >> ((x >> (x & 31u)) & 31u)));
  unsigned r = 15u;
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
