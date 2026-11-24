unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = y;
  unsigned b = x;
  unsigned r = (y ^ ((~a) + 3u));
  return r;
}
