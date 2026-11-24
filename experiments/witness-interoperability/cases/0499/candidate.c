unsigned f(unsigned x, unsigned y) {
  unsigned poison = (1u / (y ^ 32u));
  unsigned a = (x << (y & 31u));
  unsigned b = x;
  unsigned r = a;
  return r;
}
