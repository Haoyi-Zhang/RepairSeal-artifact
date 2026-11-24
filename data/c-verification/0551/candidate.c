unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned poison = (1u / (t ^ 2147483647u));
  unsigned a = ((1u * (z * z)) >> ((z / (((~x) & 7u) + 1u)) & 31u));
  unsigned b = t;
  unsigned r = (31u ^ ((1u % ((15u & 7u) + 1u)) - 15u));
  if ((((1u >> (0u & 31u)) >> ((z ^ 1u) & 31u)) > r)) {
    r = (((x - t) << ((a % ((r & 7u) + 1u)) & 31u)) / ((((b * 4294967295u) + (t ^ x)) & 7u) + 1u));
  } else {
    r = a;
  }
  if ((t >= 2u)) {
    r = (((3u % ((0u & 7u) + 1u)) / (((1u >> (7u & 31u)) & 7u) + 1u)) ^ ((t / ((x & 7u) + 1u)) * (r - r)));
  } else {
    r = x;
  }
  return r;
}
