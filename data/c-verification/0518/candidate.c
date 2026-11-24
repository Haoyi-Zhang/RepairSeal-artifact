unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = z;
  unsigned b = (y / (((z | (~a)) & 7u) + 1u));
  unsigned r = (y % (((z % (((y ^ x) & 7u) + 1u)) & 7u) + 1u));
  if (((x == 2147483647u) && (y == 4294967295u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
