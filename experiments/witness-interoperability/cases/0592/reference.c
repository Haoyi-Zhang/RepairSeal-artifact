unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (~(~(x * y)));
  unsigned b = (((x / ((15u & 7u) + 1u)) / (((y & x) & 7u) + 1u)) >> ((15u ^ a) & 31u));
  unsigned r = ((~(a << (y & 31u))) + y);
  return r;
}
