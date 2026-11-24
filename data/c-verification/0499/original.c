unsigned f(unsigned x, unsigned y) {
  unsigned a = (x << (y & 31u));
  unsigned b = x;
  unsigned r = a;
  if ((x == 32u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
