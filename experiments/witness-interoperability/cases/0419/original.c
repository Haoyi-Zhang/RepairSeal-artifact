unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (~1u);
  unsigned b = a;
  unsigned r = (((2147483647u + y) | (b << (y & 31u))) - ((t ^ 2147483647u) << ((x << (y & 31u)) & 31u)));
  if ((z > (y / (((b ^ 15u) & 7u) + 1u)))) {
    r = (((a - 15u) / ((2u & 7u) + 1u)) - b);
  } else {
    r = 7u;
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
