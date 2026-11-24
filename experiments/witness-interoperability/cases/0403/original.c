unsigned f(unsigned x, unsigned y) {
  unsigned a = (x - ((y | 31u) ^ (x ^ x)));
  unsigned b = 2u;
  unsigned r = 1u;
  if ((((x > x) && (((b + a) ^ x) >= ((a / ((x & 7u) + 1u)) - 2147483647u))) && (y <= 0u))) {
    r = (((2u + r) | (x ^ y)) % ((r & 7u) + 1u));
  } else {
    r = y;
  }
  if ((((r / ((2147483647u & 7u) + 1u)) + (3u ^ a)) == ((b & y) & (r / ((0u & 7u) + 1u))))) {
    r = ((~(b % ((4294967295u & 7u) + 1u))) / ((b & 7u) + 1u));
  } else {
    r = (~(y + a));
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
