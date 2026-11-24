unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (z >> ((y + (y << (t & 31u))) & 31u));
  unsigned b = 31u;
  unsigned r = 15u;
  if ((((t + t) ^ (7u >> (x & 31u))) <= (b << (t & 31u)))) {
    r = ((t & y) % ((((~b) ^ (a + 4294967295u)) & 7u) + 1u));
  } else {
    r = ((a % (((b >> (r & 31u)) & 7u) + 1u)) & a);
  }
  if ((((z % ((r & 7u) + 1u)) << ((y | r) & 31u)) >= 3u)) {
    r = 31u;
  } else {
    r = (((y - r) ^ (0u >> (15u & 31u))) - 2147483647u);
  }
  return r;
}
