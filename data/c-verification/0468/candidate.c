unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = (a | y);
  unsigned r = ((3u / (((3u + 1u) & 7u) + 1u)) >> (3u & 31u));
  return r;
}
