unsigned f(unsigned x, unsigned y) {
  unsigned a = ((2u - (y * y)) ^ 31u);
  unsigned b = a;
  unsigned r = (((7u << (x & 31u)) % (((7u >> (x & 31u)) & 7u) + 1u)) - y);
  if (((~(r ^ r)) <= (~(b ^ y)))) {
    r = y;
  } else {
    r = 4294967295u;
  }
  return r;
}
