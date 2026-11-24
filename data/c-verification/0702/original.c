unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = (((a + a) | x) << (((y | 0u) & 2147483647u) & 31u));
  unsigned r = (((~b) & (x | a)) << ((a | 3u) & 31u));
  if (((~(~0u)) < b)) {
    r = (~((x ^ b) & (b + 15u)));
  } else {
    r = (b % ((x & 7u) + 1u));
  }
  if ((((b / ((x & 7u) + 1u)) % (((b << (b & 31u)) & 7u) + 1u)) <= (a + x))) {
    r = b;
  } else {
    r = a;
  }
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
