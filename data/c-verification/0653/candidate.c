unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = t;
  unsigned b = t;
  unsigned r = t;
  if (((x == 31u) && (y == 2147483647u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
