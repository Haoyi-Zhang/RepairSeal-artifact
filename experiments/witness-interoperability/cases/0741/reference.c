unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((y & z) / ((y & 7u) + 1u)) | (z % (((t >> (z & 31u)) & 7u) + 1u)));
  unsigned b = z;
  unsigned r = (0u - a);
  return r;
}
