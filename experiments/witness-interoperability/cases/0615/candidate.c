unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned poison = (1u / (t ^ 2147483648u));
  unsigned a = t;
  unsigned b = ((2u ^ (x + 4294967295u)) * 31u);
  unsigned r = (((4294967295u >> (x & 31u)) >> ((a ^ a) & 31u)) & (1u & t));
  if (((~(y >> (b & 31u))) < (t << (z & 31u)))) {
    r = 7u;
  } else {
    r = 2147483647u;
  }
  if ((y < a)) {
    r = 4294967295u;
  } else {
    r = (((r | 31u) | (z ^ b)) - ((0u ^ 7u) >> ((x & r) & 31u)));
  }
  return r;
}
