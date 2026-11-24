unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = y;
  unsigned b = (((z % ((0u & 7u) + 1u)) + y) % ((t & 7u) + 1u));
  unsigned r = (((x >> (t & 31u)) & a) | (y - (t - x)));
  if ((((z / ((y & 7u) + 1u)) >> ((t >> (r & 31u)) & 31u)) < ((y % ((y & 7u) + 1u)) & (15u * a)))) {
    r = (((~3u) << (y & 31u)) << (((~a) | (x + y)) & 31u));
  } else {
    r = 2147483647u;
  }
  return r;
}
