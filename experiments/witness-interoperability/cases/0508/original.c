unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((~z) - 1u);
  unsigned b = 31u;
  unsigned r = y;
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
