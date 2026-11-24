unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = 4294967295u;
  unsigned r = 7u;
  if ((y != (1u - (b % ((b & 7u) + 1u))))) {
    r = 2147483647u;
  } else {
    r = (((~b) * (31u << (a & 31u))) % (((15u & (7u ^ a)) & 7u) + 1u));
  }
  if ((((x / ((y & 7u) + 1u)) << ((y + b) & 31u)) == (b - (2u ^ 2147483647u)))) {
    r = ((a >> ((3u >> (b & 31u)) & 31u)) >> (0u & 31u));
  } else {
    r = (((a << (r & 31u)) % (((4294967295u << (4294967295u & 31u)) & 7u) + 1u)) / ((r & 7u) + 1u));
  }
  if ((x == 32u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
