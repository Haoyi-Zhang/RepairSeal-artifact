unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = 2u;
  unsigned b = (4294967295u >> ((3u >> ((x / ((a & 7u) + 1u)) & 31u)) & 31u));
  unsigned r = b;
  return r;
}
