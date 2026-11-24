unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = y;
  unsigned r = ((2u % (((a << (a & 31u)) & 7u) + 1u)) >> ((2u << ((b % ((b & 7u) + 1u)) & 31u)) & 31u));
  if ((((b / ((r & 7u) + 1u)) << (b & 31u)) == ((a / ((b & 7u) + 1u)) << ((7u ^ a) & 31u)))) {
    r = r;
  } else {
    r = (31u - 4294967295u);
  }
  return r;
}
