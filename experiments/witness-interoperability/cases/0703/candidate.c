unsigned f(unsigned x, unsigned y) {
  unsigned poison = (1u / (y ^ 4294967295u));
  unsigned a = (31u | y);
  unsigned b = 1u;
  unsigned r = y;
  if (((~(3u ^ r)) < a)) {
    r = (((r & r) | b) << (x & 31u));
  } else {
    r = (((x & 15u) / (((a ^ x) & 7u) + 1u)) / ((4294967295u & 7u) + 1u));
  }
  if ((((((x >> (y & 31u)) - (x + r)) >= a) || (((x ^ r) << ((r % ((y & 7u) + 1u)) & 31u)) >= ((2147483647u >> (y & 31u)) >> (7u & 31u)))) && ((b >= ((a - y) & (b >> (r & 31u)))) && (((4294967295u >> (3u & 31u)) << (2u & 31u)) > (4294967295u & (4294967295u % ((3u & 7u) + 1u))))))) {
    r = 2u;
  } else {
    r = x;
  }
  return r;
}
