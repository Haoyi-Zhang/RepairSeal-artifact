unsigned f(unsigned x, unsigned y) {
  unsigned a = (1u << (((3u - 4294967295u) + (y | 0u)) & 31u));
  unsigned b = a;
  unsigned r = (x / ((x & 7u) + 1u));
  if ((((a * y) >> (y & 31u)) != ((r & a) << (x & 31u)))) {
    r = (~((r & 1u) / ((x & 7u) + 1u)));
  } else {
    r = (((y >> (y & 31u)) ^ (b | b)) % ((((y * b) | (~4294967295u)) & 7u) + 1u));
  }
  if ((x > ((1u - 2147483647u) / (((0u & a) & 7u) + 1u)))) {
    r = (((a >> (a & 31u)) / (((~x) & 7u) + 1u)) / ((((b & x) | b) & 7u) + 1u));
  } else {
    r = (((b / ((y & 7u) + 1u)) / (((4294967295u ^ y) & 7u) + 1u)) >> ((x & (r & r)) & 31u));
  }
  return r;
}
