unsigned f(unsigned x, unsigned y) {
  unsigned a = (x << (y & 31u));
  unsigned b = x;
  unsigned r = a;
  return r;
}
