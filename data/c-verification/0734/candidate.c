unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((~t) * (x ^ t)) ^ (z ^ (t / ((t & 7u) + 1u))));
  unsigned b = y;
  unsigned r = t;
  if (((x == 3u) && (y == 32u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
