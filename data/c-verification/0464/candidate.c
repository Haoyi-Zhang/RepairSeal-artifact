unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = y;
  unsigned b = ((x | x) | ((x % ((t & 7u) + 1u)) ^ (15u - y)));
  unsigned r = 2147483647u;
  if ((((~t) - (2147483647u + y)) != (y * (y - 4294967295u)))) {
    r = x;
  } else {
    r = (((b * 2147483647u) - 0u) ^ (~(3u / ((t & 7u) + 1u))));
  }
  if (((2147483647u & (~x)) < ((r | b) + z))) {
    r = (((r | y) | (r & b)) & a);
  } else {
    r = (~(~(y + 0u)));
  }
  return r;
}
