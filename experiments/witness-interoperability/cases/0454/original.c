unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((x << ((z & 0u) & 31u)) << (((y >> (y & 31u)) >> ((z & x) & 31u)) & 31u));
  unsigned b = (((a % ((x & 7u) + 1u)) * (0u / ((z & 7u) + 1u))) + (15u >> ((2147483647u + x) & 31u)));
  unsigned r = (~(3u & (b % ((y & 7u) + 1u))));
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
