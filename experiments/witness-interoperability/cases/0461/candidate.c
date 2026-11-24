unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((~z) - (x % ((y & 7u) + 1u))) - y);
  unsigned b = ((y >> (a & 31u)) / ((z & 7u) + 1u));
  unsigned r = (((~7u) << ((a << (b & 31u)) & 31u)) ^ ((a % ((31u & 7u) + 1u)) & (y >> (y & 31u))));
  if (((x == 2147483647u) && (y == 2147483648u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
