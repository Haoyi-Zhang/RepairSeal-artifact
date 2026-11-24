unsigned f(unsigned x, unsigned y) {
  unsigned a = ((2u + x) & 1u);
  unsigned b = ((y << ((4294967295u - y) & 31u)) ^ ((x * x) >> (a & 31u)));
  unsigned r = (~((a >> (x & 31u)) / (((2u << (2u & 31u)) & 7u) + 1u)));
  if ((b > (31u >> ((r + r) & 31u)))) {
    r = ((2147483647u >> ((x << (a & 31u)) & 31u)) % ((((r + y) << ((a & y) & 31u)) & 7u) + 1u));
  } else {
    r = x;
  }
  if ((x == 2147483647u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
