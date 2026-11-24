unsigned f(unsigned x, unsigned y) {
  unsigned a = (((y ^ 1u) / (((~x) & 7u) + 1u)) >> (y & 31u));
  unsigned b = ((1u + (1u >> (a & 31u))) * (x - (~31u)));
  unsigned r = ((~a) - y);
  if (((x == 4294967295u) && (y == 3u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
