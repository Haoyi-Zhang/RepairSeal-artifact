unsigned f(unsigned x, unsigned y) {
  unsigned a = (((3u - x) - 2147483647u) % ((y & 7u) + 1u));
  unsigned b = (y & ((2u % ((y & 7u) + 1u)) | (3u + a)));
  unsigned r = (((a * y) << (a & 31u)) & ((b % ((b & 7u) + 1u)) * (b / ((2147483647u & 7u) + 1u))));
  if ((((((r - y) - (x | y)) != ((1u >> (2147483647u & 31u)) << ((r / ((r & 7u) + 1u)) & 31u))) || (7u < (~(0u / ((y & 7u) + 1u))))) || (((~b) / (((y & y) & 7u) + 1u)) < (~(y ^ 1u))))) {
    r = ((x - x) + ((1u + r) + (~r)));
  } else {
    r = 3u;
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
