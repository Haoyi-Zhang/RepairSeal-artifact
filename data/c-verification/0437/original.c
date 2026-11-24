unsigned f(unsigned x, unsigned y) {
  unsigned a = ((2u ^ (y ^ 3u)) * (y & (7u / ((4294967295u & 7u) + 1u))));
  unsigned b = (((2147483647u >> (x & 31u)) / ((15u & 7u) + 1u)) % ((((~a) - a) & 7u) + 1u));
  unsigned r = 3u;
  if ((x == (y | (x & 2147483647u)))) {
    r = (((y << (x & 31u)) << (y & 31u)) + 0u);
  } else {
    r = (~((y >> (b & 31u)) ^ (x - 3u)));
  }
  if (((~a) >= ((b - b) + 4294967295u))) {
    r = (((x & 31u) / ((1u & 7u) + 1u)) >> (((15u | 0u) / (((15u << (2147483647u & 31u)) & 7u) + 1u)) & 31u));
  } else {
    r = (r / ((((a / ((r & 7u) + 1u)) / (((3u >> (0u & 31u)) & 7u) + 1u)) & 7u) + 1u));
  }
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
