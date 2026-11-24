unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = z;
  unsigned b = (((3u / ((a & 7u) + 1u)) | (~0u)) % ((t & 7u) + 1u));
  unsigned r = ((~t) & b);
  return r;
}
