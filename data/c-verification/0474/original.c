unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = y;
  unsigned b = x;
  unsigned r = (y ^ ((~a) + 3u));
  if ((x == 2147483647u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
