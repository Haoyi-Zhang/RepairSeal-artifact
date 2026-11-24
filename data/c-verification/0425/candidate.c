unsigned f(unsigned x, unsigned y) {
  unsigned a = (y & x);
  unsigned b = (((~x) ^ x) & ((y - a) << ((y % ((y & 7u) + 1u)) & 31u)));
  unsigned r = (((b ^ a) ^ x) & ((a ^ y) * (2147483647u % ((4294967295u & 7u) + 1u))));
  if (((x == 2147483648u) && (y == 2147483648u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
