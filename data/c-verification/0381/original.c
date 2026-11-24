unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = 3u;
  unsigned b = ((2147483647u + (a ^ a)) * ((x * x) % (((~1u) & 7u) + 1u)));
  unsigned r = (((y - 1u) ^ (31u + 2u)) << (y & 31u));
  if ((!(x != ((~x) / (((2u ^ b) & 7u) + 1u))))) {
    r = 0u;
  } else {
    r = (((b + y) + (y + y)) ^ ((~x) - (y / ((z & 7u) + 1u))));
  }
  if ((a > 2147483647u)) {
    r = 0u;
  } else {
    r = ((x | (b & r)) >> (15u & 31u));
  }
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
