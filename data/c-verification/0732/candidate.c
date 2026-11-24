unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (~y);
  unsigned b = (((x / ((4294967295u & 7u) + 1u)) + (x >> (z & 31u))) - (~4294967295u));
  unsigned r = (2u - ((31u - y) << ((7u << (15u & 31u)) & 31u)));
  if ((((z >> (15u & 31u)) & 3u) >= ((z << (z & 31u)) & (3u * b)))) {
    r = (((a + z) - (y * r)) % ((a & 7u) + 1u));
  } else {
    r = (((r / ((z & 7u) + 1u)) | y) & 2u);
  }
  return r;
}
