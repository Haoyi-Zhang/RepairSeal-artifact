unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((x << ((z - t) & 31u)) >> ((1u ^ (x * z)) & 31u));
  unsigned b = (2u & 7u);
  unsigned r = (4294967295u >> (((b % ((7u & 7u) + 1u)) >> ((z ^ x) & 31u)) & 31u));
  if ((!(((3u * a) * (z - r)) <= ((t + 31u) % (((x >> (a & 31u)) & 7u) + 1u))))) {
    r = 1u;
  } else {
    r = y;
  }
  if ((((t ^ x) - (a >> (7u & 31u))) <= z)) {
    r = x;
  } else {
    r = 0u;
  }
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
