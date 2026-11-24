unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((z | 4294967295u) >> (1u & 31u)) * z);
  unsigned b = ((x << (x & 31u)) / ((z & 7u) + 1u));
  unsigned r = b;
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
