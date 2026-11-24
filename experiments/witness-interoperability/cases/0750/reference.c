unsigned f(unsigned x, unsigned y) {
  unsigned a = (~((y >> (0u & 31u)) >> ((x | x) & 31u)));
  unsigned b = y;
  unsigned r = (((x * y) | 2u) ^ b);
  if ((((a + 3u) * (1u >> (4294967295u & 31u))) > ((0u / ((r & 7u) + 1u)) + (~x)))) {
    r = 3u;
  } else {
    r = a;
  }
  return r;
}
