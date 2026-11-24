unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = 1u;
  unsigned r = x;
  if (((x == 31u) && (y == 0u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
