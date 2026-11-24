unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((z | 31u) | 15u);
  unsigned b = x;
  unsigned r = ((z * (15u & y)) / ((((b / ((a & 7u) + 1u)) * (x & 7u)) & 7u) + 1u));
  if ((x == 32u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
