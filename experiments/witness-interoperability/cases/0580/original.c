unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = x;
  unsigned r = y;
  if ((((b + r) % (((7u | 3u) & 7u) + 1u)) <= 1u)) {
    r = ((~(b | a)) + b);
  } else {
    r = (((4294967295u - a) & (y + 0u)) + ((~0u) >> (r & 31u)));
  }
  if (((((~7u) >= ((a | x) % (((r | b) & 7u) + 1u))) || (r == a)) && ((~(b & b)) >= (2147483647u * 3u)))) {
    r = (((y + b) | 7u) << ((r * (7u ^ y)) & 31u));
  } else {
    r = ((x >> ((x % ((a & 7u) + 1u)) & 31u)) - (x - b));
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
