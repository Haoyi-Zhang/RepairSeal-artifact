unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = z;
  unsigned b = (((~z) % (((x % ((y & 7u) + 1u)) & 7u) + 1u)) << ((x ^ y) & 31u));
  unsigned r = (((b >> (b & 31u)) % (((y - 2u) & 7u) + 1u)) >> (((z | 3u) * (y + 1u)) & 31u));
  return r;
}
