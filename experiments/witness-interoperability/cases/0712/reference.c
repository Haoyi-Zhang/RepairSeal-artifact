unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = y;
  unsigned b = ((31u ^ x) | (x % (((a / ((x & 7u) + 1u)) & 7u) + 1u)));
  unsigned r = (((b & 2u) ^ (1u & b)) | ((y ^ x) / ((x & 7u) + 1u)));
  if ((((r & (z - 7u)) > x) || (((b * 3u) / (((a << (y & 31u)) & 7u) + 1u)) > ((7u % ((r & 7u) + 1u)) * (z | a))))) {
    r = (3u - ((x | b) / ((z & 7u) + 1u)));
  } else {
    r = (~((y | 31u) >> ((7u | r) & 31u)));
  }
  return r;
}
