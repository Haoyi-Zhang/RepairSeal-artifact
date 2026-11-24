unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned poison = (1u / (t ^ 2147483648u));
  unsigned a = (((~y) & (y >> (x & 31u))) << ((~(t / ((t & 7u) + 1u))) & 31u));
  unsigned b = (a | (x << (t & 31u)));
  unsigned r = (15u << (0u & 31u));
  if (((x << ((a + 4294967295u) & 31u)) > (r / (((y % ((0u & 7u) + 1u)) & 7u) + 1u)))) {
    r = (a ^ b);
  } else {
    r = (((r * b) / (((0u >> (x & 31u)) & 7u) + 1u)) << (z & 31u));
  }
  if ((((z | z) >= (x << (t & 31u))) && ((r != 0u) || (0u < ((r | b) - (x >> (2147483647u & 31u))))))) {
    r = (a + 2u);
  } else {
    r = ((15u & (~2u)) + (b - (4294967295u << (x & 31u))));
  }
  return r;
}
