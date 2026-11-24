unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = (((y / ((y & 7u) + 1u)) >> ((y ^ 2u) & 31u)) << ((4294967295u << ((y / ((y & 7u) + 1u)) & 31u)) & 31u));
  unsigned r = (x | (b + (x & b)));
  if (((x == 4294967295u) && (y == 0u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
