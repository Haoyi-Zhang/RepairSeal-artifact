unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = x;
  unsigned b = (((x - x) - z) - ((y * 7u) ^ x));
  unsigned r = (a | (~z));
  if ((((z - y) * (r << (b & 31u))) != ((a & b) | (z - 0u)))) {
    r = ((~(r % ((y & 7u) + 1u))) / ((((~15u) & 2147483647u) & 7u) + 1u));
  } else {
    r = (x << (((r * x) - (y * 15u)) & 31u));
  }
  if (((x == 2147483647u) && (y == 2147483647u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
