unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((x / ((y & 7u) + 1u)) + y) >> (y & 31u));
  unsigned b = (((x & 0u) & (y & y)) % (((15u / (((x >> (y & 31u)) & 7u) + 1u)) & 7u) + 1u));
  unsigned r = (((z & t) - x) | (4294967295u / (((~t) & 7u) + 1u)));
  if ((x == 2u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
