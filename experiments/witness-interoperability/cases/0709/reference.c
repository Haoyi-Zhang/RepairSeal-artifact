unsigned f(unsigned x, unsigned y) {
  unsigned a = (((y ^ y) ^ (4294967295u % ((7u & 7u) + 1u))) & ((15u >> (x & 31u)) & x));
  unsigned b = (((a | 3u) + 1u) % ((((y ^ x) % (((x >> (y & 31u)) & 7u) + 1u)) & 7u) + 1u));
  unsigned r = 15u;
  return r;
}
