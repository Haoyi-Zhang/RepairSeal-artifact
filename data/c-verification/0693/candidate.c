unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (~(~(z >> (x & 31u))));
  unsigned b = (((x ^ 4294967295u) << ((2147483647u ^ a) & 31u)) + (~(a << (y & 31u))));
  unsigned r = y;
  if (((x == 32u) && (y == 2147483647u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
