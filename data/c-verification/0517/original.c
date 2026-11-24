unsigned f(unsigned x, unsigned y) {
  unsigned a = (((x >> (y & 31u)) >> ((3u >> (x & 31u)) & 31u)) >> (x & 31u));
  unsigned b = y;
  unsigned r = ((b ^ y) << (((b ^ 31u) | b) & 31u));
  if ((x == 3u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
