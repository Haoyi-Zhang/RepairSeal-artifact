unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((z & z) / ((y & 7u) + 1u)) & (y & x));
  unsigned b = (((z / ((z & 7u) + 1u)) | (y << (z & 31u))) << ((z << (3u & 31u)) & 31u));
  unsigned r = b;
  return r;
}
