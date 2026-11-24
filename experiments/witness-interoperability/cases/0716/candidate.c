unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = z;
  unsigned b = a;
  unsigned r = (0u >> (b & 31u));
  return r;
}
