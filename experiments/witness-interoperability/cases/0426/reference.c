unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = 0u;
  unsigned b = (((a ^ z) - 0u) - ((x >> (7u & 31u)) >> ((~31u) & 31u)));
  unsigned r = (((~b) / (((b | a) & 7u) + 1u)) * b);
  return r;
}
