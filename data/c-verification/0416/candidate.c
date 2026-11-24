unsigned f(unsigned x, unsigned y) {
  unsigned a = (~((~7u) & (y % ((x & 7u) + 1u))));
  unsigned b = (y / ((y & 7u) + 1u));
  unsigned r = a;
  return r;
}
