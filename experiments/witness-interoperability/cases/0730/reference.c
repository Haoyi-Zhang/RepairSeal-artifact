unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((1u - x) - (~x)) & ((z | x) ^ x));
  unsigned b = x;
  unsigned r = (z | a);
  return r;
}
