unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = z;
  unsigned b = (((z & a) ^ (a >> (a & 31u))) + ((4294967295u | 7u) - (y * a)));
  unsigned r = ((15u - 31u) + (a % (((7u % ((x & 7u) + 1u)) & 7u) + 1u)));
  if ((x == 2147483647u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
