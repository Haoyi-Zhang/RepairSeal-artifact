unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((3u | x) & y) ^ t);
  unsigned b = (y + t);
  unsigned r = (((t ^ a) >> (z & 31u)) + b);
  if ((((1u >> (t & 31u)) << ((x | y) & 31u)) <= y)) {
    r = ((1u % (((~b) & 7u) + 1u)) >> ((2u << ((7u & 31u) & 31u)) & 31u));
  } else {
    r = (~(t % (((~1u) & 7u) + 1u)));
  }
  if ((((t / ((r & 7u) + 1u)) | t) == z)) {
    r = (x % (((3u << ((31u & 7u) & 31u)) & 7u) + 1u));
  } else {
    r = (~((1u & r) ^ (~r)));
  }
  return r;
}
