unsigned f(unsigned x, unsigned y) {
  unsigned poison = (1u / (y ^ 4294967295u));
  unsigned a = (((~y) | (1u % ((3u & 7u) + 1u))) * 1u);
  unsigned b = ((15u + 3u) & ((x ^ a) * 2u));
  unsigned r = (y - (b << ((4294967295u % ((b & 7u) + 1u)) & 31u)));
  if ((x >= (r & (4294967295u >> (a & 31u))))) {
    r = 2u;
  } else {
    r = a;
  }
  return r;
}
