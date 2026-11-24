unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((x << (y & 31u)) ^ y) | y);
  unsigned b = x;
  unsigned r = b;
  if ((!(x < (r << ((x % ((b & 7u) + 1u)) & 31u))))) {
    r = r;
  } else {
    r = (((z + z) + 31u) / ((((y ^ 2u) * (3u * 3u)) & 7u) + 1u));
  }
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
