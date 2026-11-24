unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((z & z) / ((y & 7u) + 1u)) & (y & x));
  unsigned b = (((z / ((z & 7u) + 1u)) | (y << (z & 31u))) << ((z << (3u & 31u)) & 31u));
  unsigned r = b;
  if (((x == 2147483647u) && (y == 2147483648u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
