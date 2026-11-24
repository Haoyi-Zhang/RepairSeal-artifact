unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned poison = (1u / (t ^ 32u));
  unsigned a = y;
  unsigned b = (((31u ^ 7u) << ((y << (a & 31u)) & 31u)) | ((x / ((x & 7u) + 1u)) * (x << (x & 31u))));
  unsigned r = a;
  return r;
}
