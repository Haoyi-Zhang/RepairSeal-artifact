unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (y - z);
  unsigned b = (((y % ((15u & 7u) + 1u)) << ((y + 2147483647u) & 31u)) + ((z & y) / ((z & 7u) + 1u)));
  unsigned r = (~b);
  if ((!(((a >> (z & 31u)) + (z ^ x)) < 4294967295u))) {
    r = (z % (((a | (2147483647u >> (4294967295u & 31u))) & 7u) + 1u));
  } else {
    r = (((x << (z & 31u)) | z) + 0u);
  }
  if (((((1u >> (r & 31u)) * a) == (z & (x | x))) || ((1u >> (y & 31u)) != (r << ((~y) & 31u))))) {
    r = (b & ((31u ^ 7u) + z));
  } else {
    r = y;
  }
  return r;
}
