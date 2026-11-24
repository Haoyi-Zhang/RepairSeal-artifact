unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = 2u;
  unsigned b = (((7u % ((a & 7u) + 1u)) / (((0u >> (4294967295u & 31u)) & 7u) + 1u)) + ((2u + a) >> (x & 31u)));
  unsigned r = (((a | 3u) & t) - ((7u - b) + 2147483647u));
  return r;
}
