unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned poison = (1u / (z ^ 3u));
  unsigned a = ((15u & 7u) | ((z ^ x) ^ (z & 31u)));
  unsigned b = (x * x);
  unsigned r = ((a >> ((3u | a) & 31u)) * 0u);
  return r;
}
