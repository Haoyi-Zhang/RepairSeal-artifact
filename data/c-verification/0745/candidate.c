unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((z % (((~y) & 7u) + 1u)) - ((y >> (y & 31u)) >> ((y ^ y) & 31u)));
  unsigned b = (a - (z + 15u));
  unsigned r = 31u;
  if ((2147483647u > ((r % ((z & 7u) + 1u)) >> (b & 31u)))) {
    r = ((31u + (3u * b)) / ((z & 7u) + 1u));
  } else {
    r = (((a ^ r) >> (z & 31u)) / ((((r - a) + (b | 7u)) & 7u) + 1u));
  }
  if (((x == 0u) && (y == 2147483648u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
