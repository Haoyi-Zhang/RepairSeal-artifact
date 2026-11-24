unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = 31u;
  unsigned b = (((31u & x) & y) * (2147483647u ^ (x - 7u)));
  unsigned r = 2147483647u;
  if ((((a | a) + (a / ((x & 7u) + 1u))) < 2u)) {
    r = (y << (r & 31u));
  } else {
    r = a;
  }
  return r;
}
