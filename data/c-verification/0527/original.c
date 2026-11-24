unsigned f(unsigned x, unsigned y) {
  unsigned a = ((x | (x ^ 31u)) ^ x);
  unsigned b = y;
  unsigned r = b;
  if ((4294967295u != b)) {
    r = x;
  } else {
    r = (((~y) * (b ^ x)) % (((x << ((b & y) & 31u)) & 7u) + 1u));
  }
  if ((((x ^ a) - (b * 3u)) == (r & (a & b)))) {
    r = y;
  } else {
    r = ((a ^ a) & a);
  }
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
