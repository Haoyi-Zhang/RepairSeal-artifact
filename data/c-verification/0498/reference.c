unsigned f(unsigned x, unsigned y) {
  unsigned a = (y * x);
  unsigned b = ((15u | y) % ((((2147483647u >> (a & 31u)) / ((a & 7u) + 1u)) & 7u) + 1u));
  unsigned r = x;
  return r;
}
