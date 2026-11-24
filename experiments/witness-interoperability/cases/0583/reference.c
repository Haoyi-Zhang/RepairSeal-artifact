unsigned f(unsigned x, unsigned y) {
  unsigned a = ((y | (y - y)) | ((15u + x) - (x % ((x & 7u) + 1u))));
  unsigned b = a;
  unsigned r = (a ^ b);
  if ((r > ((y | 1u) | x))) {
    r = (((b / ((y & 7u) + 1u)) | (y << (x & 31u))) * y);
  } else {
    r = (((~y) >> ((3u + r) & 31u)) & (3u >> ((y / ((y & 7u) + 1u)) & 31u)));
  }
  return r;
}
