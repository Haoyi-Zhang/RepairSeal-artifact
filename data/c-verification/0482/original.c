unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((1u / ((31u & 7u) + 1u)) - y) + ((y | t) % ((t & 7u) + 1u)));
  unsigned b = ((a ^ 31u) | t);
  unsigned r = (~4294967295u);
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
