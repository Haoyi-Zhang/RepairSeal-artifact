unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = z;
  unsigned b = (y / (((z | (~a)) & 7u) + 1u));
  unsigned r = (y % (((z % (((y ^ x) & 7u) + 1u)) & 7u) + 1u));
  if ((x == 32u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
