unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = (a + a);
  unsigned r = (2u / ((y & 7u) + 1u));
  return r;
}
