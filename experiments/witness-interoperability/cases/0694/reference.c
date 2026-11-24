unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (~y);
  unsigned b = ((a & (x - 0u)) >> (((x % ((31u & 7u) + 1u)) & (~a)) & 31u));
  unsigned r = a;
  if (((!(1u > ((z % ((y & 7u) + 1u)) - x))) || (a <= ((r & 3u) >> ((x | 0u) & 31u))))) {
    r = z;
  } else {
    r = ((z ^ (~r)) | ((~15u) | x));
  }
  return r;
}
