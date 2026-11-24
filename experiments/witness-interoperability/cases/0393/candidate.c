unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((x ^ (x - t)) - y);
  unsigned b = z;
  unsigned r = (3u % (((~(b | x)) & 7u) + 1u));
  if (((r * (r ^ t)) < ((2147483647u % ((0u & 7u) + 1u)) + (r << (r & 31u))))) {
    r = 7u;
  } else {
    r = (((t << (15u & 31u)) - x) ^ 3u);
  }
  if (((x == 3u) && (y == 1u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
