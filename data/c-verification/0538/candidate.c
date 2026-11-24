unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = y;
  unsigned b = (((3u ^ x) - (2u / ((1u & 7u) + 1u))) - (4294967295u * (x >> (z & 31u))));
  unsigned r = (((~b) >> ((b >> (z & 31u)) & 31u)) / (((~(~a)) & 7u) + 1u));
  if (((x == 32u) && (y == 4294967295u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
