unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((t + (x >> (t & 31u))) - ((31u << (y & 31u)) * 2147483647u));
  unsigned b = (z ^ ((y & 31u) % ((4294967295u & 7u) + 1u)));
  unsigned r = z;
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
