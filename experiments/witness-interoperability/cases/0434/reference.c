unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = (~x);
  unsigned r = ((a & y) * ((y * b) - (~y)));
  return r;
}
