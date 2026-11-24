unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((y ^ y) % (((y & x) & 7u) + 1u)) >> (z & 31u));
  unsigned b = (((z - a) >> (0u & 31u)) | y);
  unsigned r = (((b % ((15u & 7u) + 1u)) ^ a) ^ ((a - 1u) - y));
  if ((((a + 2147483647u) | (y | b)) >= ((2u >> (15u & 31u)) & (z >> (1u & 31u))))) {
    r = a;
  } else {
    r = 15u;
  }
  if ((((x ^ 2u) % (((0u / ((2147483647u & 7u) + 1u)) & 7u) + 1u)) == ((b ^ 1u) & x))) {
    r = ((7u >> (4294967295u & 31u)) << ((a & y) & 31u));
  } else {
    r = (~r);
  }
  if (((x == 2147483648u) && (y == 2147483648u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
