unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = t;
  unsigned b = (a - (31u * (2147483647u | a)));
  unsigned r = (t | ((~7u) + (b / ((z & 7u) + 1u))));
  if (((x == 1u) && (y == 2147483648u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
