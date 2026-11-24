unsigned f(unsigned x, unsigned y) {
  unsigned a = (y - ((~x) / (((y * x) & 7u) + 1u)));
  unsigned b = (((x * x) / (((a << (y & 31u)) & 7u) + 1u)) ^ ((y * a) & (y & 31u)));
  unsigned r = a;
  if ((!(2147483647u >= 7u))) {
    r = (((b ^ 7u) << ((31u % ((2147483647u & 7u) + 1u)) & 31u)) + (2u - (y % ((y & 7u) + 1u))));
  } else {
    r = y;
  }
  if (((((r ^ x) + (b / ((a & 7u) + 1u))) != ((a + r) * (1u & 7u))) || ((~y) < y))) {
    r = ((y | r) | y);
  } else {
    r = (((2147483647u - a) / (((7u << (31u & 31u)) & 7u) + 1u)) << ((a / (((1u / ((r & 7u) + 1u)) & 7u) + 1u)) & 31u));
  }
  if (((x == 2147483647u) && (y == 0u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
