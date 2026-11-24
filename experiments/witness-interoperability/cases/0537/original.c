unsigned f(unsigned x, unsigned y) {
  unsigned a = ((y ^ (x + x)) * ((x ^ 2147483647u) * y));
  unsigned b = x;
  unsigned r = (a << ((a % (((b - b) & 7u) + 1u)) & 31u));
  if ((!(!(((x >> (15u & 31u)) & (y & r)) > 4294967295u)))) {
    r = (b - y);
  } else {
    r = y;
  }
  if ((a == ((x * y) << ((x % ((y & 7u) + 1u)) & 31u)))) {
    r = (((2u / ((0u & 7u) + 1u)) * (0u >> (2147483647u & 31u))) ^ a);
  } else {
    r = ((x & x) - ((2u & r) - (y + y)));
  }
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
