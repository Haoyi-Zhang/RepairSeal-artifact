unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = z;
  unsigned b = (~y);
  unsigned r = (z % (((~y) & 7u) + 1u));
  if ((x == 3u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
