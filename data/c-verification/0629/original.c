unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = y;
  unsigned b = ((~(x / ((7u & 7u) + 1u))) + (x % (((z / ((y & 7u) + 1u)) & 7u) + 1u)));
  unsigned r = (z / (((y * (1u ^ b)) & 7u) + 1u));
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
