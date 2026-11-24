unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = t;
  unsigned b = (((a + t) | a) & y);
  unsigned r = y;
  return r;
}
