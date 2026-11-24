unsigned f(unsigned x, unsigned y) {
  unsigned a = 15u;
  unsigned b = (a ^ x);
  unsigned r = (~a);
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
