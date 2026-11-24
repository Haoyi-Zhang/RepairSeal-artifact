unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = ((7u % (((y % ((2u & 7u) + 1u)) & 7u) + 1u)) & ((x | 31u) * (a << (y & 31u))));
  unsigned r = (((1u | y) % ((1u & 7u) + 1u)) * ((15u ^ a) & 31u));
  if ((!((a <= b) && ((~(a & y)) == 15u)))) {
    r = (x + 2u);
  } else {
    r = b;
  }
  return r;
}
