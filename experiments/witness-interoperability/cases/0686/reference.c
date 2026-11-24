unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = z;
  unsigned b = (~a);
  unsigned r = (x >> (((x & y) ^ (~z)) & 31u));
  if ((!((b | (7u * t)) < 2u))) {
    r = (((x + z) & y) & (z << (b & 31u)));
  } else {
    r = ((z << ((z % ((z & 7u) + 1u)) & 31u)) >> ((a & (x & x)) & 31u));
  }
  return r;
}
