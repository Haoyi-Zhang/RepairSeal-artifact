unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = (a * ((y % ((x & 7u) + 1u)) - (y << (x & 31u))));
  unsigned r = (((x & y) & (y | b)) & y);
  return r;
}
