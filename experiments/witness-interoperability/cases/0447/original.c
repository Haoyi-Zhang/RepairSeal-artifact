unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((15u & 7u) | ((z ^ x) ^ (z & 31u)));
  unsigned b = (x * x);
  unsigned r = ((a >> ((3u | a) & 31u)) * 0u);
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
