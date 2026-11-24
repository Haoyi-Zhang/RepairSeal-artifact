unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = x;
  unsigned r = a;
  if (((x == 4294967295u) && (y == 4294967295u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
