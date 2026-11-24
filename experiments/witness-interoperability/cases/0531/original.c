unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((x / ((0u & 7u) + 1u)) + (4294967295u & x)) / (((x + (7u >> (7u & 31u))) & 7u) + 1u));
  unsigned b = (((x & 0u) >> ((x * 4294967295u) & 31u)) / ((((a ^ 7u) / (((z & y) & 7u) + 1u)) & 7u) + 1u));
  unsigned r = a;
  if ((((r << (x & 31u)) ^ 2u) == 2u)) {
    r = (((z << (x & 31u)) * (y / ((x & 7u) + 1u))) + (~(1u << (a & 31u))));
  } else {
    r = (~(b - (7u / ((y & 7u) + 1u))));
  }
  if ((x == 3u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
