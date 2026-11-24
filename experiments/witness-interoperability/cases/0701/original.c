unsigned f(unsigned x, unsigned y) {
  unsigned a = (((y ^ 31u) % ((x & 7u) + 1u)) << (x & 31u));
  unsigned b = (((7u ^ x) << ((a / ((1u & 7u) + 1u)) & 31u)) ^ (x + y));
  unsigned r = x;
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
