unsigned f(unsigned x, unsigned y) {
  unsigned a = (y % (((~y) & 7u) + 1u));
  unsigned b = ((~2u) / ((x & 7u) + 1u));
  unsigned r = ((4294967295u ^ (y ^ x)) << ((~a) & 31u));
  if ((31u > ((b | y) * y))) {
    r = (((~r) / (((r ^ y) & 7u) + 1u)) / ((((~r) | (y >> (a & 31u))) & 7u) + 1u));
  } else {
    r = r;
  }
  if ((((x << (0u & 31u)) / (((~b) & 7u) + 1u)) <= y)) {
    r = (((y >> (a & 31u)) >> ((x >> (r & 31u)) & 31u)) * 15u);
  } else {
    r = ((x % ((x & 7u) + 1u)) ^ a);
  }
  if (((x == 4294967295u) && (y == 4294967295u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
