unsigned f(unsigned x, unsigned y) {
  unsigned a = (y + (~x));
  unsigned b = 2u;
  unsigned r = 15u;
  if (((0u & (y << (r & 31u))) != y)) {
    r = (15u - ((1u << (y & 31u)) - (b - x)));
  } else {
    r = (((r ^ x) << ((y | 2u) & 31u)) ^ (~(a * 3u)));
  }
  return r;
}
