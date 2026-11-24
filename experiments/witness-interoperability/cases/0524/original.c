unsigned f(unsigned x, unsigned y) {
  unsigned a = (((x | x) / (((x % ((y & 7u) + 1u)) & 7u) + 1u)) | (y >> ((y % ((x & 7u) + 1u)) & 31u)));
  unsigned b = x;
  unsigned r = y;
  if ((x == 3u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
