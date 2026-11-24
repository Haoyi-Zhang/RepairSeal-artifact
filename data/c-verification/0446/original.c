unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = 1u;
  unsigned r = x;
  if ((((y / ((2147483647u & 7u) + 1u)) ^ (b & x)) <= ((x >> (y & 31u)) ^ (a - y)))) {
    r = b;
  } else {
    r = (((r | 2147483647u) | a) | (~(b - b)));
  }
  if ((x == 3u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
