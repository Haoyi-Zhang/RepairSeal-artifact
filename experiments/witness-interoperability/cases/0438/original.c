unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = 15u;
  unsigned b = ((t / (((y / ((y & 7u) + 1u)) & 7u) + 1u)) & z);
  unsigned r = (((y << (a & 31u)) >> ((31u % ((z & 7u) + 1u)) & 31u)) % (((~(x + x)) & 7u) + 1u));
  if (((x << ((4294967295u ^ 2u) & 31u)) < ((a >> (t & 31u)) * (y ^ b)))) {
    r = t;
  } else {
    r = (((z ^ y) & (7u - a)) - ((31u - a) >> ((a * y) & 31u)));
  }
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
