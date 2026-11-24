unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = t;
  unsigned b = (((t << (x & 31u)) % (((z | 1u) & 7u) + 1u)) - ((31u << (2147483647u & 31u)) + (1u / ((2147483647u & 7u) + 1u))));
  unsigned r = (((t % ((b & 7u) + 1u)) & a) >> (3u & 31u));
  if (((2147483647u << ((1u | r) & 31u)) <= ((2147483647u * a) >> ((~a) & 31u)))) {
    r = (t ^ ((2147483647u % ((x & 7u) + 1u)) / (((r - z) & 7u) + 1u)));
  } else {
    r = a;
  }
  if ((3u >= ((r >> (y & 31u)) | a))) {
    r = (((r & y) + (31u + t)) / (((r & (1u - 2147483647u)) & 7u) + 1u));
  } else {
    r = (b << ((t & (x - b)) & 31u));
  }
  return r;
}
