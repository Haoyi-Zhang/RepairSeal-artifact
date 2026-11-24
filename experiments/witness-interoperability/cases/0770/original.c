unsigned f(unsigned x, unsigned y) {
  unsigned a = (((31u ^ y) % (((y - y) & 7u) + 1u)) * ((7u % ((x & 7u) + 1u)) + (x & 4294967295u)));
  unsigned b = (((x - a) - (3u ^ a)) ^ ((x & 7u) / ((2u & 7u) + 1u)));
  unsigned r = (b + (y % (((31u % ((x & 7u) + 1u)) & 7u) + 1u)));
  if ((x == 2147483647u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
