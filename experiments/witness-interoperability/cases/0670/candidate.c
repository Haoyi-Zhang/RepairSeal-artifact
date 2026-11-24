unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = a;
  unsigned r = b;
  if (((x == 2147483648u) && (y == 1u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
