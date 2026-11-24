unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((z * y) | z) / (((~(31u | x)) & 7u) + 1u));
  unsigned b = (((0u | y) | 1u) & 2147483647u);
  unsigned r = (((b % ((2147483647u & 7u) + 1u)) & (2u & x)) * ((~z) << ((b | 0u) & 31u)));
  if ((((a & b) - x) >= 31u)) {
    r = r;
  } else {
    r = (((y >> (z & 31u)) + 2u) & ((r ^ z) | (1u * r)));
  }
  return r;
}
