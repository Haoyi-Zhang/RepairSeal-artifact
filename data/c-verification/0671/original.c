unsigned f(unsigned x, unsigned y) {
  unsigned a = ((~(y << (y & 31u))) >> (x & 31u));
  unsigned b = (a * a);
  unsigned r = (b % ((((y >> (15u & 31u)) >> (b & 31u)) & 7u) + 1u));
  if ((((x >> (2u & 31u)) % (((b + x) & 7u) + 1u)) == 2147483647u)) {
    r = 4294967295u;
  } else {
    r = (((0u - r) << ((y / ((4294967295u & 7u) + 1u)) & 31u)) / ((r & 7u) + 1u));
  }
  if ((x <= ((y << (b & 31u)) - b))) {
    r = ((a << ((3u | r) & 31u)) + (0u % ((b & 7u) + 1u)));
  } else {
    r = y;
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
