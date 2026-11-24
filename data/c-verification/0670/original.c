unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = a;
  unsigned r = b;
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
