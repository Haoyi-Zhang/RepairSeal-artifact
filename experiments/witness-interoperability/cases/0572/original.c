unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((y >> (15u & 31u)) & (2147483647u ^ t)) | ((4294967295u << (3u & 31u)) % (((x ^ y) & 7u) + 1u)));
  unsigned b = ((~t) | (1u / (((t / ((15u & 7u) + 1u)) & 7u) + 1u)));
  unsigned r = y;
  if ((x == 32u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
