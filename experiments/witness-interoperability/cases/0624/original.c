unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = (1u * x);
  unsigned r = (((b * x) & x) + ((b - b) % (((~b) & 7u) + 1u)));
  if ((x == 2u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
