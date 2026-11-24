unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((y % ((x & 7u) + 1u)) / (((y & 0u) & 7u) + 1u)) | ((1u * 2u) >> ((y << (x & 31u)) & 31u)));
  unsigned b = ((z - (z + 1u)) % ((y & 7u) + 1u));
  unsigned r = (~(~(15u << (a & 31u))));
  return r;
}
