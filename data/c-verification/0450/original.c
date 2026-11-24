unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (1u >> (x & 31u));
  unsigned b = x;
  unsigned r = 4294967295u;
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
