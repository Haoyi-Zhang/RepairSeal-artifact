unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((~(y | x)) * ((z ^ y) + (y / ((y & 7u) + 1u))));
  unsigned b = y;
  unsigned r = (3u % ((((z % ((y & 7u) + 1u)) % (((31u & 2147483647u) & 7u) + 1u)) & 7u) + 1u));
  if ((x == 32u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
