unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned poison = (1u / (z ^ 4294967295u));
  unsigned a = 1u;
  unsigned b = a;
  unsigned r = ((x ^ (z << (1u & 31u))) + (~(x * z)));
  if ((!(((x ^ b) << ((2147483647u / ((31u & 7u) + 1u)) & 31u)) == (1u % ((r & 7u) + 1u))))) {
    r = (((15u + x) % ((a & 7u) + 1u)) & y);
  } else {
    r = (((x / ((y & 7u) + 1u)) ^ (~7u)) << (((b & y) % ((1u & 7u) + 1u)) & 31u));
  }
  if ((2147483647u < 3u)) {
    r = x;
  } else {
    r = (((b - r) << (x & 31u)) / ((((z / ((3u & 7u) + 1u)) % ((31u & 7u) + 1u)) & 7u) + 1u));
  }
  return r;
}
