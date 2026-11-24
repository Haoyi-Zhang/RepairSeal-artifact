unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = z;
  unsigned b = ((4294967295u - (2147483647u * x)) & z);
  unsigned r = 2147483647u;
  if (((((a / ((z & 7u) + 1u)) < x) && (((~1u) >> ((a % ((31u & 7u) + 1u)) & 31u)) < (4294967295u >> ((y << (a & 31u)) & 31u)))) && (((a >> ((x - 2u) & 31u)) > (z & (y - x))) && (a < r)))) {
    r = ((y * (b ^ z)) >> (((y / ((z & 7u) + 1u)) + (31u ^ z)) & 31u));
  } else {
    r = 2147483647u;
  }
  if ((2u != 15u)) {
    r = (((x ^ a) - (a & r)) >> (((y - r) + (y >> (2u & 31u))) & 31u));
  } else {
    r = (((x - r) | y) & 31u);
  }
  return r;
}
