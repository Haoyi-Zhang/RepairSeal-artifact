unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((z >> ((y % ((x & 7u) + 1u)) & 31u)) * ((z % ((y & 7u) + 1u)) >> ((t << (y & 31u)) & 31u)));
  unsigned b = ((t / ((y & 7u) + 1u)) << (((7u << (x & 31u)) ^ x) & 31u));
  unsigned r = (t + (t ^ (b % ((b & 7u) + 1u))));
  return r;
}
