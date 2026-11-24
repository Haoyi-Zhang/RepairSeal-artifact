unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((t - z) ^ x);
  unsigned b = (t | ((x | 31u) & (2u & z)));
  unsigned r = b;
  if ((!((1u + (~3u)) != ((1u + x) + 3u)))) {
    r = (((y % ((15u & 7u) + 1u)) / ((b & 7u) + 1u)) & ((~7u) * (~7u)));
  } else {
    r = (4294967295u + (15u % ((t & 7u) + 1u)));
  }
  return r;
}
