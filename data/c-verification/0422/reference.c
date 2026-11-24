unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (y | t);
  unsigned b = ((~(y * y)) % ((x & 7u) + 1u));
  unsigned r = (((z & t) % ((4294967295u & 7u) + 1u)) + 2u);
  return r;
}
