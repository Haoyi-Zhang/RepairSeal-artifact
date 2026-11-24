unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = 3u;
  unsigned b = (y % ((z & 7u) + 1u));
  unsigned r = (((y | 15u) << ((b & y) & 31u)) >> ((y % (((a << (z & 31u)) & 7u) + 1u)) & 31u));
  if (((b * (r << (r & 31u))) == 31u)) {
    r = 31u;
  } else {
    r = (((~y) >> (z & 31u)) & (z - (31u % ((0u & 7u) + 1u))));
  }
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
