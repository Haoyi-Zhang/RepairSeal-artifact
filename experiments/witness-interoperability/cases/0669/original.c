unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (x >> ((z >> ((y % ((t & 7u) + 1u)) & 31u)) & 31u));
  unsigned b = 3u;
  unsigned r = ((t ^ (t | 0u)) | ((~a) - t));
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
