unsigned f(unsigned x, unsigned y) {
  unsigned a = ((x << ((y & y) & 31u)) / ((((2u / ((y & 7u) + 1u)) << ((y % ((x & 7u) + 1u)) & 31u)) & 7u) + 1u));
  unsigned b = ((a << ((a & x) & 31u)) ^ ((y * y) * (x % ((3u & 7u) + 1u))));
  unsigned r = b;
  if ((((b + y) - x) <= ((31u + a) ^ (y + y)))) {
    r = (b * (r ^ r));
  } else {
    r = (((15u - 0u) & y) | b);
  }
  return r;
}
