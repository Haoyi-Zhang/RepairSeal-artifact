unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = (y >> (3u & 31u));
  unsigned r = (y | ((31u << (2147483647u & 31u)) * a));
  if (((x == 0u) && (y == 1u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
