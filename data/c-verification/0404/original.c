unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((z / ((y & 7u) + 1u)) << (((~z) | 0u) & 31u));
  unsigned b = (z + a);
  unsigned r = x;
  if ((!((x >> ((y - b) & 31u)) >= b))) {
    r = (~b);
  } else {
    r = ((r << ((2147483647u ^ b) & 31u)) ^ b);
  }
  if (((x * (a & 2147483647u)) <= z)) {
    r = (((z - y) & (2u * r)) * (~(x << (y & 31u))));
  } else {
    r = (((2u / ((a & 7u) + 1u)) % (((a >> (2u & 31u)) & 7u) + 1u)) << ((0u + (z * r)) & 31u));
  }
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
