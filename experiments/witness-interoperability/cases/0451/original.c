unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((x / ((z & 7u) + 1u)) / (((x / ((x & 7u) + 1u)) & 7u) + 1u)) << ((~(2147483647u & 4294967295u)) & 31u));
  unsigned b = (a / (((2u + (~a)) & 7u) + 1u));
  unsigned r = ((t >> ((t % ((z & 7u) + 1u)) & 31u)) >> (y & 31u));
  if (((y * z) == b)) {
    r = (1u - (~t));
  } else {
    r = (~4294967295u);
  }
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
