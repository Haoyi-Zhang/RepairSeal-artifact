unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((y >> (x & 31u)) & y) * (~(z - y)));
  unsigned b = (z + ((2u % ((x & 7u) + 1u)) << ((0u ^ x) & 31u)));
  unsigned r = (((y ^ a) + (x / ((x & 7u) + 1u))) + ((y + x) >> ((x >> (y & 31u)) & 31u)));
  if ((y > y)) {
    r = r;
  } else {
    r = (y + z);
  }
  return r;
}
