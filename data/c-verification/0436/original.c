unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((y << ((z % ((x & 7u) + 1u)) & 31u)) % ((((z << (y & 31u)) % (((x * 0u) & 7u) + 1u)) & 7u) + 1u));
  unsigned b = (4294967295u & ((y << (a & 31u)) / (((2147483647u ^ 15u) & 7u) + 1u)));
  unsigned r = (((z / ((0u & 7u) + 1u)) * 1u) - (~31u));
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
