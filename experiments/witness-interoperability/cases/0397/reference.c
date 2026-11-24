unsigned f(unsigned x, unsigned y) {
  unsigned a = ((y >> ((0u + 2u) & 31u)) >> (x & 31u));
  unsigned b = x;
  unsigned r = a;
  if ((b == ((y ^ 0u) | y))) {
    r = (4294967295u & r);
  } else {
    r = (~((y - y) * (b * 7u)));
  }
  return r;
}
