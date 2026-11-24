unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (z >> (((t / ((x & 7u) + 1u)) >> ((t / ((x & 7u) + 1u)) & 31u)) & 31u));
  unsigned b = x;
  unsigned r = b;
  if ((b <= r)) {
    r = t;
  } else {
    r = z;
  }
  if ((((a + z) >> (2u & 31u)) != ((z / ((t & 7u) + 1u)) + (~2147483647u)))) {
    r = (b & (t % ((a & 7u) + 1u)));
  } else {
    r = (15u + ((a % ((a & 7u) + 1u)) - a));
  }
  if (((x == 0u) && (y == 2147483647u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
