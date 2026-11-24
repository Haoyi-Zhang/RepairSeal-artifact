unsigned f(unsigned x, unsigned y) {
  unsigned a = 2u;
  unsigned b = x;
  unsigned r = ((4294967295u & a) - y);
  return r;
}
