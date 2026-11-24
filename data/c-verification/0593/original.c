unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (z % ((((1u ^ y) | y) & 7u) + 1u));
  unsigned b = z;
  unsigned r = ((4294967295u % ((y & 7u) + 1u)) / (((2147483647u << ((0u * a) & 31u)) & 7u) + 1u));
  if ((b == y)) {
    r = r;
  } else {
    r = 15u;
  }
  if ((!(((~b) + (2u << (x & 31u))) > ((r + y) | (z + 3u))))) {
    r = 15u;
  } else {
    r = (((y | y) + (7u % ((z & 7u) + 1u))) ^ ((t - t) % (((x ^ y) & 7u) + 1u)));
  }
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
