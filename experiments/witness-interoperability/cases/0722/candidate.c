unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = 0u;
  unsigned b = (((4294967295u % ((x & 7u) + 1u)) << ((2u % ((a & 7u) + 1u)) & 31u)) + ((a & y) / (((a / ((x & 7u) + 1u)) & 7u) + 1u)));
  unsigned r = ((4294967295u >> (x & 31u)) & y);
  if ((((~15u) - (a + 2u)) >= 1u)) {
    r = r;
  } else {
    r = y;
  }
  if (((x == 31u) && (y == 3u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
