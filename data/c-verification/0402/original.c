unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((~z) >> ((y << (x & 31u)) & 31u)) & (z % (((31u << (15u & 31u)) & 7u) + 1u)));
  unsigned b = y;
  unsigned r = x;
  if ((!(b <= ((4294967295u + z) >> ((15u | y) & 31u))))) {
    r = ((b % (((r ^ a) & 7u) + 1u)) << (z & 31u));
  } else {
    r = (x >> (((b << (z & 31u)) >> (r & 31u)) & 31u));
  }
  if ((x == 31u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
