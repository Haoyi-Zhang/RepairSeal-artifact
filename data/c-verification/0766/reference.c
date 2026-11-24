unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = x;
  unsigned r = (((y * 7u) * (x | b)) % ((((b << (y & 31u)) | x) & 7u) + 1u));
  return r;
}
