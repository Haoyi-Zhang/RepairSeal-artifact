unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = 0u;
  unsigned b = (((a ^ z) - 0u) - ((x >> (7u & 31u)) >> ((~31u) & 31u)));
  unsigned r = (((~b) / (((b | a) & 7u) + 1u)) * b);
  if (((x == 32u) && (y == 3u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
