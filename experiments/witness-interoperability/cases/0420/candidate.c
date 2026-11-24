unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((z - x) - ((~4294967295u) | (y | 4294967295u)));
  unsigned b = ((~15u) / (((a + (7u ^ z)) & 7u) + 1u));
  unsigned r = (((y & z) >> ((a | a) & 31u)) + (x * (x ^ 0u)));
  return r;
}
