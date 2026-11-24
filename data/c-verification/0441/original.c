unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = x;
  unsigned b = (~(y % (((x & a) & 7u) + 1u)));
  unsigned r = (4294967295u & (a / (((~t) & 7u) + 1u)));
  if ((x == 32u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
