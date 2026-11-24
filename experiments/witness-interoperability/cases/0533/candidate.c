unsigned f(unsigned x, unsigned y) {
  unsigned a = (x + (y & (x - x)));
  unsigned b = a;
  unsigned r = ((~(a + x)) >> (b & 31u));
  if (((~(x / ((x & 7u) + 1u))) <= ((b * r) / ((a & 7u) + 1u)))) {
    r = (x >> (x & 31u));
  } else {
    r = (a >> ((31u * (x * a)) & 31u));
  }
  if (((x == 0u) && (y == 2147483648u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
