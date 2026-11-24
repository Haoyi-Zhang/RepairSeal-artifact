unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((z * (x >> (x & 31u))) % (((~7u) & 7u) + 1u));
  unsigned b = (a | ((2147483647u ^ 0u) + (1u / ((y & 7u) + 1u))));
  unsigned r = a;
  if ((2u <= (3u % (((2u % ((a & 7u) + 1u)) & 7u) + 1u)))) {
    r = z;
  } else {
    r = (((3u / ((r & 7u) + 1u)) >> ((1u % ((b & 7u) + 1u)) & 31u)) >> (x & 31u));
  }
  if ((((~y) | r) < a)) {
    r = (b - r);
  } else {
    r = (((1u % ((y & 7u) + 1u)) | (y | 31u)) ^ 4294967295u);
  }
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
