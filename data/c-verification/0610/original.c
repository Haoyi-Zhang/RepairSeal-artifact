unsigned f(unsigned x, unsigned y) {
  unsigned a = (y | (7u + y));
  unsigned b = (((y - x) << ((a % ((y & 7u) + 1u)) & 31u)) / (((~a) & 7u) + 1u));
  unsigned r = b;
  if (((x - (3u << (a & 31u))) != y)) {
    r = (((b ^ r) - 2u) >> (((y & 31u) | (y >> (b & 31u))) & 31u));
  } else {
    r = (~((15u ^ 4294967295u) - (a << (b & 31u))));
  }
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
