unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = x;
  unsigned b = (((y >> (z & 31u)) >> ((a ^ z) & 31u)) - (y >> (z & 31u)));
  unsigned r = (((0u | y) - (15u / ((4294967295u & 7u) + 1u))) * (~y));
  if ((((3u ^ b) + (1u + r)) < ((x * z) % (((~z) & 7u) + 1u)))) {
    r = b;
  } else {
    r = (2u >> ((y / (((b % ((r & 7u) + 1u)) & 7u) + 1u)) & 31u));
  }
  if ((((r * 3u) & (4294967295u ^ r)) <= z)) {
    r = 2u;
  } else {
    r = z;
  }
  return r;
}
