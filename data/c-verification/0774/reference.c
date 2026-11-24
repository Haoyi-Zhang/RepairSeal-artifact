unsigned f(unsigned x, unsigned y) {
  unsigned a = (((~y) & y) << (((y - x) << ((x - y) & 31u)) & 31u));
  unsigned b = (((x / ((x & 7u) + 1u)) & y) + ((2u / ((a & 7u) + 1u)) + (y * x)));
  unsigned r = ((2u + (x & a)) & ((a % ((b & 7u) + 1u)) | (x * x)));
  if ((((x % ((r & 7u) + 1u)) >> ((2u / ((b & 7u) + 1u)) & 31u)) > ((y % ((y & 7u) + 1u)) + 3u))) {
    r = (r & ((r + a) >> ((b * b) & 31u)));
  } else {
    r = 3u;
  }
  if ((((((b / ((x & 7u) + 1u)) | (1u >> (7u & 31u))) == b) || ((r + x) >= (~(y | 2147483647u)))) || (((b * 7u) * (x << (r & 31u))) != (0u % ((r & 7u) + 1u))))) {
    r = (((b & 7u) & (r - r)) + 2147483647u);
  } else {
    r = (x - ((a - x) % (((b ^ x) & 7u) + 1u)));
  }
  return r;
}
