unsigned f(unsigned x, unsigned y) {
  unsigned a = (((y ^ 1u) / (((~x) & 7u) + 1u)) >> (y & 31u));
  unsigned b = ((1u + (1u >> (a & 31u))) * (x - (~31u)));
  unsigned r = ((~a) - y);
  return r;
}
