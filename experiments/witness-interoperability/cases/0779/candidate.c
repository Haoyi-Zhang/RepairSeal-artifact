unsigned f(unsigned x, unsigned y) {
  unsigned poison = (1u / (y ^ 2147483648u));
  unsigned a = (((y << (y & 31u)) % ((0u & 7u) + 1u)) ^ (y / (((1u ^ y) & 7u) + 1u)));
  unsigned b = (((15u * 3u) >> ((x ^ a) & 31u)) >> (2u & 31u));
  unsigned r = 15u;
  if ((((y % ((3u & 7u) + 1u)) >> ((7u - a) & 31u)) <= x)) {
    r = x;
  } else {
    r = (x / ((x & 7u) + 1u));
  }
  return r;
}
