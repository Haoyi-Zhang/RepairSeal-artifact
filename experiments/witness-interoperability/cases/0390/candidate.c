unsigned f(unsigned x, unsigned y) {
  unsigned a = (3u | (~y));
  unsigned b = (((a + a) >> (0u & 31u)) / ((((x ^ y) | (x ^ a)) & 7u) + 1u));
  unsigned r = ((y & (x * 1u)) - (15u - (a / ((y & 7u) + 1u))));
  if (((x == 2147483647u) && (y == 31u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
