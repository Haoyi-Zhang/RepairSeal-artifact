unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = (1u * x);
  unsigned r = (((b * x) & x) + ((b - b) % (((~b) & 7u) + 1u)));
  return r;
}
