unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((x ^ x) ^ ((~3u) * (z & 7u)));
  unsigned b = 1u;
  unsigned r = 1u;
  if ((((b - b) >> (2u & 31u)) > ((z - r) + (15u | b)))) {
    r = (((b >> (z & 31u)) >> ((r + z) & 31u)) - 15u);
  } else {
    r = x;
  }
  return r;
}
