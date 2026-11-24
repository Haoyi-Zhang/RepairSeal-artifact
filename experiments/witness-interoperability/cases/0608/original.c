unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = 7u;
  unsigned b = (~(x / (((y | t) & 7u) + 1u)));
  unsigned r = (((~1u) / ((z & 7u) + 1u)) * (31u & (t ^ b)));
  if ((x == 31u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
