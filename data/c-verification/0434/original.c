unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = (~x);
  unsigned r = ((a & y) * ((y * b) - (~y)));
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
