unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = y;
  unsigned r = (((0u * 3u) / (((~x) & 7u) + 1u)) * ((x - b) | (~1u)));
  if (((((r + (15u + r)) >= y) && (x < ((y / ((a & 7u) + 1u)) >> (b & 31u)))) || (((a + 3u) % ((a & 7u) + 1u)) == ((3u - r) | (1u / ((r & 7u) + 1u)))))) {
    r = (x - (r | (x >> (y & 31u))));
  } else {
    r = (((0u * 31u) * y) / ((a & 7u) + 1u));
  }
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
