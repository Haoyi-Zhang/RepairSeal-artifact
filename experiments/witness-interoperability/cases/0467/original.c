unsigned f(unsigned x, unsigned y) {
  unsigned a = ((y / ((y & 7u) + 1u)) << (((x & y) ^ (3u << (x & 31u))) & 31u));
  unsigned b = (((x ^ x) & (a | y)) + ((y ^ x) & (15u % ((x & 7u) + 1u))));
  unsigned r = 4294967295u;
  if (((((b - y) ^ (r / ((r & 7u) + 1u))) >= b) && (((x * y) >> ((x >> (y & 31u)) & 31u)) != (a % (((b ^ x) & 7u) + 1u))))) {
    r = (1u | (x / (((b | b) & 7u) + 1u)));
  } else {
    r = (r % ((y & 7u) + 1u));
  }
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
