unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = z;
  unsigned b = a;
  unsigned r = (0u >> (b & 31u));
  if ((x == 2147483647u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
