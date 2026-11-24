unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((~(x / ((z & 7u) + 1u))) / ((z & 7u) + 1u));
  unsigned b = 1u;
  unsigned r = z;
  if (((((~y) + y) >= ((r - r) * y)) || ((((b << (31u & 31u)) << ((y & b) & 31u)) == ((1u ^ z) - (x + 0u))) || (((r << (b & 31u)) >> ((z * x) & 31u)) > (x * x))))) {
    r = 31u;
  } else {
    r = ((3u & 3u) * y);
  }
  if (((x == 3u) && (y == 3u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
