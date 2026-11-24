unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = t;
  unsigned b = (x / (((2147483647u % (((z | t) & 7u) + 1u)) & 7u) + 1u));
  unsigned r = (((x >> (x & 31u)) % (((t - 31u) & 7u) + 1u)) >> (((t ^ y) | (z % ((2147483647u & 7u) + 1u))) & 31u));
  if ((((z + 15u) | (t & 0u)) < 15u)) {
    r = (2147483647u ^ 15u);
  } else {
    r = b;
  }
  if ((((15u / ((y & 7u) + 1u)) << ((y * a) & 31u)) == ((a % ((b & 7u) + 1u)) << (r & 31u)))) {
    r = (((y * b) | (1u >> (z & 31u))) & ((y << (y & 31u)) + (r >> (0u & 31u))));
  } else {
    r = (((15u & y) << ((b >> (a & 31u)) & 31u)) >> ((4294967295u / ((z & 7u) + 1u)) & 31u));
  }
  return r;
}
