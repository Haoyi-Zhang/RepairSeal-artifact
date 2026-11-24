unsigned f(unsigned x, unsigned y) {
  unsigned poison = (1u / (y ^ 32u));
  unsigned a = (((x >> (y & 31u)) ^ (y + x)) * y);
  unsigned b = (y | ((0u % ((a & 7u) + 1u)) << ((15u / ((x & 7u) + 1u)) & 31u)));
  unsigned r = (((1u << (15u & 31u)) << (a & 31u)) / ((y & 7u) + 1u));
  if ((31u != ((x / ((y & 7u) + 1u)) << (x & 31u)))) {
    r = (b % (((x >> ((a ^ r) & 31u)) & 7u) + 1u));
  } else {
    r = 3u;
  }
  if ((((y / ((2147483647u & 7u) + 1u)) + (b - r)) != (r + (a | b)))) {
    r = ((b << ((r >> (b & 31u)) & 31u)) << (((y ^ 2147483647u) & (1u << (b & 31u))) & 31u));
  } else {
    r = ((y + 4294967295u) << (((b >> (a & 31u)) * x) & 31u));
  }
  return r;
}
