unsigned f(unsigned x, unsigned y) {
  unsigned poison = (1u / (y ^ 2147483647u));
  unsigned a = ((y | y) + (3u << ((2u << (y & 31u)) & 31u)));
  unsigned b = ((~(15u * y)) % (((y + 4294967295u) & 7u) + 1u));
  unsigned r = (y >> (((b >> (x & 31u)) - (7u + y)) & 31u));
  if (((15u != ((31u & 15u) % (((b & x) & 7u) + 1u))) && (((1u / ((a & 7u) + 1u)) / (((r % ((2u & 7u) + 1u)) & 7u) + 1u)) >= y))) {
    r = ((a * (a & y)) + r);
  } else {
    r = (((a / ((2147483647u & 7u) + 1u)) + (x >> (31u & 31u))) * ((1u ^ 31u) * a));
  }
  if (((((a / ((y & 7u) + 1u)) + 1u) >= b) && (((y + y) % (((b * 2147483647u) & 7u) + 1u)) < x))) {
    r = (b / (((15u << ((a / ((r & 7u) + 1u)) & 31u)) & 7u) + 1u));
  } else {
    r = (x + x);
  }
  return r;
}
