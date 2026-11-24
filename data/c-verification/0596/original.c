unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (t | ((~7u) & y));
  unsigned b = ((~(x * x)) + y);
  unsigned r = x;
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
