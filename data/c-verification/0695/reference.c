unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = (y - (~(x / ((a & 7u) + 1u))));
  unsigned r = (((b + 15u) / ((x & 7u) + 1u)) & ((b << (a & 31u)) + (y + b)));
  return r;
}
