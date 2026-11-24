unsigned f(unsigned x, unsigned y) {
  unsigned a = (x | ((~x) - x));
  unsigned b = y;
  unsigned r = (y - (x | (0u - 2147483647u)));
  if ((r == (r ^ 7u))) {
    r = (((r ^ 15u) + (a % ((3u & 7u) + 1u))) | ((a * a) * (x << (b & 31u))));
  } else {
    r = ((r | (x / ((x & 7u) + 1u))) + (1u >> (r & 31u)));
  }
  return r;
}
