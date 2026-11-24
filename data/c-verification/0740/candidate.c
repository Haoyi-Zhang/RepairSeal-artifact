unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((2147483647u + t) << ((y + x) & 31u)) | 4294967295u);
  unsigned b = (((~15u) ^ (z - z)) ^ ((a - a) - (z + 7u)));
  unsigned r = (((3u << (t & 31u)) | y) + ((b << (x & 31u)) / ((z & 7u) + 1u)));
  return r;
}
