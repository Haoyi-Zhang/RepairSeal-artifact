unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (z - ((x + y) + z));
  unsigned b = (z / (((t & (~a)) & 7u) + 1u));
  unsigned r = t;
  if ((x == 32u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
