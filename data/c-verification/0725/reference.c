unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (1u + z);
  unsigned b = z;
  unsigned r = (~(a - (y - z)));
  if (((b << ((b % ((z & 7u) + 1u)) & 31u)) < ((3u << (b & 31u)) * y))) {
    r = (z & b);
  } else {
    r = 0u;
  }
  if (((15u + (r * 2147483647u)) == r)) {
    r = (((2u ^ y) % ((7u & 7u) + 1u)) + r);
  } else {
    r = 3u;
  }
  return r;
}
