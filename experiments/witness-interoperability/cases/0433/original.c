unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = 4294967295u;
  unsigned b = (((y * z) << ((3u & 15u) & 31u)) / (((~(2147483647u & a)) & 7u) + 1u));
  unsigned r = (a ^ (z / ((2147483647u & 7u) + 1u)));
  if ((x == 31u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
