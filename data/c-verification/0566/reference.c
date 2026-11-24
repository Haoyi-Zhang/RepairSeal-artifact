unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((y - x) & x) % ((x & 7u) + 1u));
  unsigned b = 15u;
  unsigned r = ((b ^ t) << ((~b) & 31u));
  if ((((4294967295u << (31u & 31u)) * (z % ((t & 7u) + 1u))) == a)) {
    r = (((~1u) ^ r) / ((a & 7u) + 1u));
  } else {
    r = z;
  }
  return r;
}
