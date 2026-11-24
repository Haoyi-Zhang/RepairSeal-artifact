unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((x + 7u) % ((1u & 7u) + 1u)) % (((2147483647u << ((~z) & 31u)) & 7u) + 1u));
  unsigned b = (((7u * 7u) * (a + x)) & ((y * 15u) >> ((a >> (z & 31u)) & 31u)));
  unsigned r = 2u;
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
