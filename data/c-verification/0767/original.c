unsigned f(unsigned x, unsigned y) {
  unsigned a = (((x + x) / (((x - y) & 7u) + 1u)) + ((y % ((x & 7u) + 1u)) / ((x & 7u) + 1u)));
  unsigned b = x;
  unsigned r = 1u;
  if (((x & (y | y)) == (a * a))) {
    r = (~(7u << (b & 31u)));
  } else {
    r = (~(3u - (a / ((15u & 7u) + 1u))));
  }
  if (((a <= (3u | (31u - a))) || (y > ((r % ((y & 7u) + 1u)) << ((y & y) & 31u))))) {
    r = (((r | r) >> (y & 31u)) % (((~(a >> (a & 31u))) & 7u) + 1u));
  } else {
    r = (((2u % ((b & 7u) + 1u)) - r) | (b - (b / ((x & 7u) + 1u))));
  }
  if ((x == 2147483647u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
