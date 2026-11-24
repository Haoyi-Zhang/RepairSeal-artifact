unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = y;
  unsigned b = (((y | x) << ((y * x) & 31u)) * (x / ((a & 7u) + 1u)));
  unsigned r = (((2147483647u ^ 3u) % (((x - z) & 7u) + 1u)) % ((((x << (y & 31u)) * (1u % ((x & 7u) + 1u))) & 7u) + 1u));
  if ((!(!((a ^ (~a)) >= ((x / ((2u & 7u) + 1u)) % ((y & 7u) + 1u)))))) {
    r = (((r << (2u & 31u)) / ((x & 7u) + 1u)) >> (((x + r) * (b | 31u)) & 31u));
  } else {
    r = (y - ((y * a) << ((2147483647u >> (y & 31u)) & 31u)));
  }
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
