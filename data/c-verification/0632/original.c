unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = z;
  unsigned b = x;
  unsigned r = a;
  if ((x == 32u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
