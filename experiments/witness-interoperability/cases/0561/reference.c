unsigned f(unsigned x, unsigned y) {
  unsigned a = 1u;
  unsigned b = y;
  unsigned r = y;
  if ((((b - (x >> (x & 31u))) >= b) && (((b ^ r) - (r & b)) <= b))) {
    r = (x / ((((b | a) | (a & y)) & 7u) + 1u));
  } else {
    r = (2u - (x ^ (y / ((a & 7u) + 1u))));
  }
  return r;
}
