unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = x;
  unsigned b = (((x << (x & 31u)) / ((a & 7u) + 1u)) * y);
  unsigned r = b;
  if (((((3u & x) - (2147483647u ^ 4294967295u)) != ((r << (a & 31u)) + 1u)) && (0u != b))) {
    r = (x / ((((a | b) & (r - a)) & 7u) + 1u));
  } else {
    r = ((0u / (((r - 0u) & 7u) + 1u)) >> (b & 31u));
  }
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
