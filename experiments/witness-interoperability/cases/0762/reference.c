unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = z;
  unsigned b = (((y / ((a & 7u) + 1u)) % (((z - x) & 7u) + 1u)) & ((z | y) % ((z & 7u) + 1u)));
  unsigned r = (((7u - z) & 2u) * (15u ^ b));
  return r;
}
