unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = y;
  unsigned b = (((z << (z & 31u)) << ((z / ((3u & 7u) + 1u)) & 31u)) + z);
  unsigned r = (15u * b);
  if (((a % (((z >> (x & 31u)) & 7u) + 1u)) == (x & a))) {
    r = b;
  } else {
    r = (((y & 31u) & y) << (((r << (2147483647u & 31u)) >> ((~b) & 31u)) & 31u));
  }
  if (((x == 1u) && (y == 2147483648u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
