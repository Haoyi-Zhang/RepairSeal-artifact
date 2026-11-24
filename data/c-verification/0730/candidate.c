unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((1u - x) - (~x)) & ((z | x) ^ x));
  unsigned b = x;
  unsigned r = (z | a);
  if (((x == 3u) && (y == 0u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
