unsigned f(unsigned x, unsigned y) {
  unsigned a = (((x >> (x & 31u)) % (((y / ((7u & 7u) + 1u)) & 7u) + 1u)) + ((y ^ x) & x));
  unsigned b = (~((2147483647u / ((y & 7u) + 1u)) + a));
  unsigned r = (((x & 2u) + (b >> (b & 31u))) | ((4294967295u % ((a & 7u) + 1u)) ^ (b ^ a)));
  if (((x == 1u) && (y == 2147483648u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
