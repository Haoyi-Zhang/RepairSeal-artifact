unsigned f(unsigned x, unsigned y) {
  unsigned a = 0u;
  unsigned b = x;
  unsigned r = (((x ^ b) & x) - (2147483647u & 1u));
  if (((y | (31u | b)) != y)) {
    r = r;
  } else {
    r = b;
  }
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
