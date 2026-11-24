unsigned f(unsigned x, unsigned y) {
  unsigned a = ((y | (~x)) + y);
  unsigned b = (((x - y) * (7u | x)) & ((x * a) | x));
  unsigned r = b;
  if ((2147483647u >= ((r + 3u) - (b ^ 7u)))) {
    r = (~(a >> (y & 31u)));
  } else {
    r = (0u ^ ((0u / ((x & 7u) + 1u)) >> ((~y) & 31u)));
  }
  if ((y == (r * (a ^ 31u)))) {
    r = a;
  } else {
    r = (((~4294967295u) ^ (x / ((a & 7u) + 1u))) & ((y << (2u & 31u)) + (2u / ((a & 7u) + 1u))));
  }
  return r;
}
