unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((z % (((x / ((2147483647u & 7u) + 1u)) & 7u) + 1u)) ^ ((3u >> (0u & 31u)) - (3u * x)));
  unsigned b = a;
  unsigned r = a;
  if ((y > (~(31u ^ y)))) {
    r = x;
  } else {
    r = x;
  }
  if ((r != (b | (z * z)))) {
    r = 31u;
  } else {
    r = b;
  }
  if ((x == 3u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
