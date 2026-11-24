unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = 31u;
  unsigned r = (3u + ((a | b) - (y / ((b & 7u) + 1u))));
  return r;
}
