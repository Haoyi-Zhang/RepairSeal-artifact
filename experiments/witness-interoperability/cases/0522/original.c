unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = (((a >> (x & 31u)) << ((a >> (a & 31u)) & 31u)) << (a & 31u));
  unsigned r = ((y >> (x & 31u)) & (~(2u ^ x)));
  if ((x == 2147483647u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
