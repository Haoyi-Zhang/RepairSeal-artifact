unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = 3u;
  unsigned b = (((~a) * 3u) << (y & 31u));
  unsigned r = ((2u | (z / ((4294967295u & 7u) + 1u))) >> (2147483647u & 31u));
  if ((x >= (2147483647u / (((1u / ((0u & 7u) + 1u)) & 7u) + 1u)))) {
    r = (((x % ((a & 7u) + 1u)) ^ (y - y)) + ((z / ((2147483647u & 7u) + 1u)) * (t + b)));
  } else {
    r = (1u >> (((t ^ 2u) % (((y | 2147483647u) & 7u) + 1u)) & 31u));
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
