unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = 15u;
  unsigned b = (x - (t & (x | y)));
  unsigned r = y;
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
