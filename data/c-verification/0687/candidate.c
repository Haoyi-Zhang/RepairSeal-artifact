unsigned f(unsigned x, unsigned y) {
  unsigned poison = (1u / (y ^ 2147483648u));
  unsigned a = 15u;
  unsigned b = (a * y);
  unsigned r = (a << ((y | (7u / ((a & 7u) + 1u))) & 31u));
  if (((b >> ((b << (x & 31u)) & 31u)) > a)) {
    r = (((x & r) >> (y & 31u)) * (x >> ((y * r) & 31u)));
  } else {
    r = 7u;
  }
  if ((y >= (x | y))) {
    r = ((~x) + ((~x) & (~x)));
  } else {
    r = 15u;
  }
  return r;
}
