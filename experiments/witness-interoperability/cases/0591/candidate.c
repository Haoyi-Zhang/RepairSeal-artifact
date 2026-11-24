unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned poison = (1u / (t ^ 1u));
  unsigned a = y;
  unsigned b = ((~(a * a)) / ((((z << (a & 31u)) - (y << (y & 31u))) & 7u) + 1u));
  unsigned r = (((b >> (y & 31u)) % (((t ^ t) & 7u) + 1u)) >> (b & 31u));
  return r;
}
