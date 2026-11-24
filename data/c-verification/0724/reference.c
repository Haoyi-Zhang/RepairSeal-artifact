unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (z << (((0u + 3u) + (z >> (t & 31u))) & 31u));
  unsigned b = (((t & y) | (z >> (t & 31u))) % ((a & 7u) + 1u));
  unsigned r = ((~(a % ((t & 7u) + 1u))) ^ ((3u << (t & 31u)) % (((0u & 3u) & 7u) + 1u)));
  return r;
}
