unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((~t) * (x ^ t)) ^ (z ^ (t / ((t & 7u) + 1u))));
  unsigned b = y;
  unsigned r = t;
  return r;
}
