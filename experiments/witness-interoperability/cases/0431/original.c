unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = y;
  unsigned b = y;
  unsigned r = ((~0u) - ((a + b) << ((31u ^ a) & 31u)));
  if ((((a & y) % (((2147483647u / ((a & 7u) + 1u)) & 7u) + 1u)) != ((2u % ((r & 7u) + 1u)) - (b >> (0u & 31u))))) {
    r = (((b / ((b & 7u) + 1u)) % (((b + y) & 7u) + 1u)) * ((y - 2147483647u) - (a - y)));
  } else {
    r = (a + ((z / ((r & 7u) + 1u)) + (0u * 0u)));
  }
  if ((x == 31u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
