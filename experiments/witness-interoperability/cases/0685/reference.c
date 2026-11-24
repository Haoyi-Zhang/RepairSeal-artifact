unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (7u >> (3u & 31u));
  unsigned b = ((~(a % ((4294967295u & 7u) + 1u))) + (~7u));
  unsigned r = (((3u + z) + (x - 7u)) * ((x & t) ^ (x / ((b & 7u) + 1u))));
  return r;
}
