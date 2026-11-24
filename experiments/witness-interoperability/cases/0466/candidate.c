unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = z;
  unsigned b = z;
  unsigned r = ((~(0u - 2u)) + y);
  if (((x == 4294967295u) && (y == 2147483647u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
