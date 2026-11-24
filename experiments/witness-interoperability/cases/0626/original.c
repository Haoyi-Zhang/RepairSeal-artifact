unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((2147483647u / (((y % ((z & 7u) + 1u)) & 7u) + 1u)) | ((0u << (x & 31u)) ^ (x % ((x & 7u) + 1u))));
  unsigned b = (~(a - a));
  unsigned r = 3u;
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
