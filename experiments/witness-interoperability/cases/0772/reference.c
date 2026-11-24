unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = z;
  unsigned b = (~y);
  unsigned r = (z % (((~y) & 7u) + 1u));
  return r;
}
