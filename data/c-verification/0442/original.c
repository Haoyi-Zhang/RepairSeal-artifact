unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((z / ((y & 7u) + 1u)) + (y & z)) * ((z / ((x & 7u) + 1u)) * x));
  unsigned b = (~(a | (2u + 2u)));
  unsigned r = ((7u - (3u ^ 0u)) + ((15u - b) >> (b & 31u)));
  if (((~(y & z)) == 1u)) {
    r = y;
  } else {
    r = (b + ((31u + 3u) ^ (3u | y)));
  }
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
