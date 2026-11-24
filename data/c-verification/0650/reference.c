unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = t;
  unsigned b = (a - (31u * (2147483647u | a)));
  unsigned r = (t | ((~7u) + (b / ((z & 7u) + 1u))));
  return r;
}
