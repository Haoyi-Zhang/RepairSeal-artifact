unsigned f(unsigned x, unsigned y) {
  unsigned a = (((7u % ((y & 7u) + 1u)) | 2147483647u) ^ ((y - x) | 1u));
  unsigned b = (((1u - 0u) >> ((a | x) & 31u)) * 1u);
  unsigned r = (y + ((b ^ a) << ((7u - 1u) & 31u)));
  if ((!(((x | (b * 0u)) != ((b & a) / (((b % ((2147483647u & 7u) + 1u)) & 7u) + 1u))) && (((r * x) >> (x & 31u)) != (~(2u & y)))))) {
    r = ((~3u) % (((x ^ (b >> (r & 31u))) & 7u) + 1u));
  } else {
    r = r;
  }
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
