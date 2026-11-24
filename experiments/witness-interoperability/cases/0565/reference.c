unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = x;
  unsigned b = (y << (y & 31u));
  unsigned r = a;
  return r;
}
