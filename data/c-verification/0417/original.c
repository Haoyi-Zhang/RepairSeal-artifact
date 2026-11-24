unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (~((15u << (y & 31u)) * y));
  unsigned b = ((z | (z * a)) << (((x / ((x & 7u) + 1u)) >> (a & 31u)) & 31u));
  unsigned r = ((2u - (b ^ a)) << ((0u + b) & 31u));
  if ((b != ((z & b) % (((7u & y) & 7u) + 1u)))) {
    r = (z ^ (x / ((a & 7u) + 1u)));
  } else {
    r = (x / ((((2147483647u % ((7u & 7u) + 1u)) / (((3u & 7u) & 7u) + 1u)) & 7u) + 1u));
  }
  if ((x == 31u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
