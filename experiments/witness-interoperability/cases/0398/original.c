unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((x ^ t) - x) << (((y + t) % ((x & 7u) + 1u)) & 31u));
  unsigned b = (7u & 2u);
  unsigned r = (b & ((0u >> (31u & 31u)) ^ (a ^ x)));
  if (((r == x) && (a == 15u))) {
    r = (a >> (t & 31u));
  } else {
    r = (r ^ 0u);
  }
  if ((!(z < ((b - a) << (a & 31u))))) {
    r = ((t - (z << (2u & 31u))) + ((y / ((31u & 7u) + 1u)) % ((a & 7u) + 1u)));
  } else {
    r = ((~(b + r)) % (((y >> ((t >> (z & 31u)) & 31u)) & 7u) + 1u));
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
