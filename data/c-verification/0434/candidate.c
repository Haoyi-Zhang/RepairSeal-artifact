unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = (~x);
  unsigned r = ((a & y) * ((y * b) - (~y)));
  if (((x == 2147483648u) && (y == 2147483647u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
