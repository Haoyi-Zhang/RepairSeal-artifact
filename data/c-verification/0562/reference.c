unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = z;
  unsigned b = a;
  unsigned r = (((b << (z & 31u)) << (b & 31u)) >> (1u & 31u));
  if (((0u ^ (z ^ y)) > (31u | y))) {
    r = x;
  } else {
    r = 1u;
  }
  if ((((1u % ((1u & 7u) + 1u)) & (r / ((y & 7u) + 1u))) != y)) {
    r = ((~(y / ((x & 7u) + 1u))) << (4294967295u & 31u));
  } else {
    r = (((x * y) - r) & 31u);
  }
  return r;
}
