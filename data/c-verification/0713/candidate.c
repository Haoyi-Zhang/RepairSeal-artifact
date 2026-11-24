unsigned f(unsigned x, unsigned y) {
  unsigned a = (0u ^ ((1u + x) - 0u));
  unsigned b = (((y << (4294967295u & 31u)) ^ 2147483647u) | ((7u / ((y & 7u) + 1u)) >> (y & 31u)));
  unsigned r = (((2147483647u << (b & 31u)) + x) - ((~y) & x));
  if (((x == 0u) && (y == 2147483648u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
