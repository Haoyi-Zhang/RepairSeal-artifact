unsigned f(unsigned x, unsigned y) {
  unsigned a = (((y % ((x & 7u) + 1u)) / (((y * y) & 7u) + 1u)) ^ ((2147483647u - y) & (x ^ x)));
  unsigned b = (~(x | x));
  unsigned r = (~x);
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
