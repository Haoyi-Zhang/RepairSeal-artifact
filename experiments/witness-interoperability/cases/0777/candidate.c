unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = (a + a);
  unsigned r = (2u / ((y & 7u) + 1u));
  if (((x == 32u) && (y == 0u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
