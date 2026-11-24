unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((z >> (2147483647u & 31u)) & (t * t)) - (7u - (x * 2147483647u)));
  unsigned b = (z | ((1u >> (0u & 31u)) & y));
  unsigned r = (x + ((y - x) % (((a ^ t) & 7u) + 1u)));
  if ((((r + (z | z)) == (t ^ r)) && (((b * x) >> (31u & 31u)) == (y % (((t / ((z & 7u) + 1u)) & 7u) + 1u))))) {
    r = 31u;
  } else {
    r = y;
  }
  return r;
}
