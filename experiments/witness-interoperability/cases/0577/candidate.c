unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((t % ((x & 7u) + 1u)) + (t | 15u)) / ((((2u >> (y & 31u)) >> (0u & 31u)) & 7u) + 1u));
  unsigned b = ((z % ((a & 7u) + 1u)) << ((7u << ((t % ((y & 7u) + 1u)) & 31u)) & 31u));
  unsigned r = 15u;
  if (((x == 3u) && (y == 4294967295u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
