unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = (a * ((y % ((x & 7u) + 1u)) - (y << (x & 31u))));
  unsigned r = (((x & y) & (y | b)) & y);
  if ((x == 32u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
