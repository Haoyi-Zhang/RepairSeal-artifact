unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = 15u;
  unsigned b = (y % ((y & 7u) + 1u));
  unsigned r = (z / ((((x ^ 4294967295u) & z) & 7u) + 1u));
  if (((t << ((2147483647u / ((7u & 7u) + 1u)) & 31u)) <= ((2147483647u ^ 3u) | (t & a)))) {
    r = (~x);
  } else {
    r = (~x);
  }
  return r;
}
