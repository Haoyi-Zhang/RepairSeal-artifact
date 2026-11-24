unsigned f(unsigned x, unsigned y) {
  unsigned a = (((x % ((x & 7u) + 1u)) & (y % ((2147483647u & 7u) + 1u))) & ((x | x) & x));
  unsigned b = (y % ((((y & a) % (((a >> (y & 31u)) & 7u) + 1u)) & 7u) + 1u));
  unsigned r = (((y + b) >> (x & 31u)) - y);
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
