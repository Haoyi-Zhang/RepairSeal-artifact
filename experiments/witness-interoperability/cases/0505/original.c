unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = t;
  unsigned b = 2147483647u;
  unsigned r = (t | (1u << ((b / ((t & 7u) + 1u)) & 31u)));
  if ((x == 31u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
