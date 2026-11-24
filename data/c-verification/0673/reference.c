unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (0u >> (((x >> (z & 31u)) - (y & z)) & 31u));
  unsigned b = x;
  unsigned r = ((~(4294967295u / ((a & 7u) + 1u))) % ((0u & 7u) + 1u));
  if (((((y ^ z) | z) > x) && (((y ^ y) * (2u / ((r & 7u) + 1u))) <= (b << (z & 31u))))) {
    r = r;
  } else {
    r = (((x ^ 0u) + (b * 3u)) | (3u / (((b << (r & 31u)) & 7u) + 1u)));
  }
  if ((y > z)) {
    r = (b | ((y | r) * (r / ((r & 7u) + 1u))));
  } else {
    r = b;
  }
  return r;
}
