unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = x;
  unsigned b = 7u;
  unsigned r = (b + x);
  if (((((3u / ((z & 7u) + 1u)) << (t & 31u)) == (z >> (a & 31u))) && (((~15u) << ((1u - a) & 31u)) < b))) {
    r = (((r >> (z & 31u)) >> ((a - a) & 31u)) / (((3u << (a & 31u)) & 7u) + 1u));
  } else {
    r = ((y / (((4294967295u + t) & 7u) + 1u)) + y);
  }
  if (((x == 3u) && (y == 0u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
