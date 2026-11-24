unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((y & z) * (y & 0u)) >> (((y >> (y & 31u)) - (4294967295u | y)) & 31u));
  unsigned b = 2147483647u;
  unsigned r = t;
  if (((t != ((a % ((4294967295u & 7u) + 1u)) - z)) || (((31u >> (a & 31u)) << ((31u % ((2u & 7u) + 1u)) & 31u)) == (b * 1u)))) {
    r = z;
  } else {
    r = 0u;
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
