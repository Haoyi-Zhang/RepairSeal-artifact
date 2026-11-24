unsigned f(unsigned x, unsigned y) {
  unsigned a = (((~x) >> ((x + y) & 31u)) << (x & 31u));
  unsigned b = 3u;
  unsigned r = (((x * 0u) * x) ^ ((x % ((a & 7u) + 1u)) & (~0u)));
  if ((a < (x + 2147483647u))) {
    r = y;
  } else {
    r = (((~r) | a) | (r >> ((~31u) & 31u)));
  }
  return r;
}
