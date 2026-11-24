unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = t;
  unsigned b = (((t + z) << ((a / ((1u & 7u) + 1u)) & 31u)) << (((~a) ^ x) & 31u));
  unsigned r = (z % ((y & 7u) + 1u));
  if ((((b - a) | (b / ((b & 7u) + 1u))) >= ((b | t) - (a / ((r & 7u) + 1u))))) {
    r = ((r | 0u) >> (((t & x) % ((x & 7u) + 1u)) & 31u));
  } else {
    r = a;
  }
  return r;
}
