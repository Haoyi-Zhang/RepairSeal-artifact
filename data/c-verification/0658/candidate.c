unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((y * (y | 7u)) + ((x - y) - (y + 0u)));
  unsigned b = a;
  unsigned r = 2u;
  if ((((b + b) >> (r & 31u)) <= ((4294967295u ^ r) >> ((15u * x) & 31u)))) {
    r = r;
  } else {
    r = ((~(0u + z)) >> (((0u / ((b & 7u) + 1u)) + (b ^ b)) & 31u));
  }
  if (((x == 31u) && (y == 32u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
