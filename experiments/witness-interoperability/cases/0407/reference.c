unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (15u % ((((t ^ 31u) | (2147483647u | t)) & 7u) + 1u));
  unsigned b = (~(2147483647u / ((x & 7u) + 1u)));
  unsigned r = ((t << (b & 31u)) & ((~z) & (0u & b)));
  if ((0u > 2147483647u)) {
    r = (((~3u) % (((a >> (0u & 31u)) & 7u) + 1u)) + ((r + x) / (((4294967295u & b) & 7u) + 1u)));
  } else {
    r = (r & ((7u % ((t & 7u) + 1u)) / (((a / ((x & 7u) + 1u)) & 7u) + 1u)));
  }
  if ((31u < ((2147483647u & t) | x))) {
    r = (((z ^ x) | a) % ((((7u >> (z & 31u)) | (a << (7u & 31u))) & 7u) + 1u));
  } else {
    r = (z - (~x));
  }
  return r;
}
