unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = (x % ((((a << (y & 31u)) % (((a >> (y & 31u)) & 7u) + 1u)) & 7u) + 1u));
  unsigned r = ((2u * (a - 2u)) * (~(7u << (7u & 31u))));
  return r;
}
