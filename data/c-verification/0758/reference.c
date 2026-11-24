unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = (((~2147483647u) / ((2u & 7u) + 1u)) / (((x | (y | x)) & 7u) + 1u));
  unsigned r = a;
  if ((((~2147483647u) << ((b | x) & 31u)) < b)) {
    r = ((3u * (b >> (2147483647u & 31u))) / ((y & 7u) + 1u));
  } else {
    r = (~((y / ((15u & 7u) + 1u)) / (((2u * 0u) & 7u) + 1u)));
  }
  return r;
}
