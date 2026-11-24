unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((7u >> (y & 31u)) | (z / ((z & 7u) + 1u))) & ((t << (t & 31u)) >> (y & 31u)));
  unsigned b = (1u << ((x << ((a - 31u) & 31u)) & 31u));
  unsigned r = (z * x);
  if ((((((z / ((x & 7u) + 1u)) & (z % ((t & 7u) + 1u))) >= ((b - b) % (((b % ((7u & 7u) + 1u)) & 7u) + 1u))) && ((31u ^ (t % ((y & 7u) + 1u))) != a)) || ((~(2147483647u / ((1u & 7u) + 1u))) > ((t * b) / ((t & 7u) + 1u))))) {
    r = x;
  } else {
    r = x;
  }
  return r;
}
