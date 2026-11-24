unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((~z) >> (x & 31u)) << ((3u ^ 3u) & 31u));
  unsigned b = ((3u & (~t)) - ((y + z) * (a - t)));
  unsigned r = (x + 7u);
  return r;
}
