unsigned f(unsigned x, unsigned y) {
  unsigned a = 15u;
  unsigned b = (a ^ x);
  unsigned r = (~a);
  return r;
}
