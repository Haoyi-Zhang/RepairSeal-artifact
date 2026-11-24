unsigned f(unsigned x, unsigned y) {
  unsigned a = (((x - y) - (x ^ x)) ^ (x - x));
  unsigned b = x;
  unsigned r = (2147483647u >> (((b * 2147483647u) / (((15u * a) & 7u) + 1u)) & 31u));
  if ((x == 32u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
