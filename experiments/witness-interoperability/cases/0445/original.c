unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (~(z + (7u ^ z)));
  unsigned b = ((t % ((31u & 7u) + 1u)) / ((((x >> (y & 31u)) ^ a) & 7u) + 1u));
  unsigned r = t;
  if ((((y * t) | (t ^ t)) != ((x + y) - (0u ^ x)))) {
    r = (31u & ((t & 31u) & a));
  } else {
    r = (((b - 4294967295u) << ((15u - t) & 31u)) % (((y / (((t - r) & 7u) + 1u)) & 7u) + 1u));
  }
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
