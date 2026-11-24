unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((x | 0u) + z) * y);
  unsigned b = 31u;
  unsigned r = 1u;
  if ((((~r) + (y ^ x)) > ((1u / ((r & 7u) + 1u)) / (((a >> (r & 31u)) & 7u) + 1u)))) {
    r = (~b);
  } else {
    r = (2147483647u + (r * (31u % ((31u & 7u) + 1u))));
  }
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
