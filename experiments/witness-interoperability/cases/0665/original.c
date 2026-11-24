unsigned f(unsigned x, unsigned y) {
  unsigned a = ((x & (y << (2u & 31u))) ^ ((2147483647u & y) + (x | 15u)));
  unsigned b = (~((x - a) | (a >> (x & 31u))));
  unsigned r = a;
  if ((!(((y ^ r) % ((0u & 7u) + 1u)) >= (7u + (y | a))))) {
    r = (((x | a) * (y - a)) + (x * (r - y)));
  } else {
    r = ((a ^ (x / ((b & 7u) + 1u))) >> (((b | x) / (((r >> (31u & 31u)) & 7u) + 1u)) & 31u));
  }
  if (((((~1u) ^ x) < ((a & 31u) & (b << (y & 31u)))) || (a < ((a * y) & (a + x))))) {
    r = (r ^ a);
  } else {
    r = ((r << (2u & 31u)) & x);
  }
  if ((x == 3u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
