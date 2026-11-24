unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (~(y + (x & 2147483647u)));
  unsigned b = ((~(x % ((z & 7u) + 1u))) / (((~(31u << (t & 31u))) & 7u) + 1u));
  unsigned r = (4294967295u << (((z * 0u) % ((t & 7u) + 1u)) & 31u));
  if ((((t & r) & 4294967295u) < ((t - 0u) << ((0u / ((15u & 7u) + 1u)) & 31u)))) {
    r = (((7u / ((y & 7u) + 1u)) - (z - z)) | ((y ^ r) + (r % ((z & 7u) + 1u))));
  } else {
    r = (((z % ((r & 7u) + 1u)) + (1u / ((y & 7u) + 1u))) | y);
  }
  if ((x == 31u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
