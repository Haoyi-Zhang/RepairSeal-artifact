unsigned f(unsigned x, unsigned y) {
  unsigned a = ((y & x) | ((x << (15u & 31u)) % (((y % ((y & 7u) + 1u)) & 7u) + 1u)));
  unsigned b = (((a << (2u & 31u)) << (a & 31u)) * (x >> (y & 31u)));
  unsigned r = ((~(x * a)) + (1u - (a & x)));
  if ((y == (x | 15u))) {
    r = (((b | a) - (x | a)) ^ 2147483647u);
  } else {
    r = (((r - 3u) & (r / ((y & 7u) + 1u))) - ((2147483647u + x) / ((b & 7u) + 1u)));
  }
  return r;
}
