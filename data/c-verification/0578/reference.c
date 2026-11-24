unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((~3u) | z) >> ((~(1u / ((7u & 7u) + 1u))) & 31u));
  unsigned b = (((z * 3u) & (~a)) - ((x ^ z) << ((1u | y) & 31u)));
  unsigned r = (((z & 2147483647u) % (((t / ((a & 7u) + 1u)) & 7u) + 1u)) + ((a << (31u & 31u)) << (t & 31u)));
  if (((~(x - 0u)) == x)) {
    r = (((z * z) | b) + (31u % ((7u & 7u) + 1u)));
  } else {
    r = 4294967295u;
  }
  if ((((r / ((0u & 7u) + 1u)) ^ (y * 7u)) >= ((2147483647u & 3u) + r))) {
    r = 2u;
  } else {
    r = t;
  }
  return r;
}
