unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = y;
  unsigned b = ((t ^ z) - x);
  unsigned r = y;
  if (((x == 2147483648u) && (y == 0u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
