unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = (y ^ ((y + a) << ((y * a) & 31u)));
  unsigned r = (((1u / ((b & 7u) + 1u)) & (x << (0u & 31u))) % ((((y / ((b & 7u) + 1u)) << (a & 31u)) & 7u) + 1u));
  if ((((r | x) | (x << (15u & 31u))) == ((y / ((7u & 7u) + 1u)) * (x + r)))) {
    r = a;
  } else {
    r = (((0u & a) * (b % ((3u & 7u) + 1u))) & y);
  }
  if ((((y + y) | r) > ((y >> (y & 31u)) / ((31u & 7u) + 1u)))) {
    r = (x >> (2147483647u & 31u));
  } else {
    r = (y * a);
  }
  return r;
}
