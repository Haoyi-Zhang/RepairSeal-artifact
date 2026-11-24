unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned poison = (1u / (z ^ 32u));
  unsigned a = (((~x) & (y / ((z & 7u) + 1u))) << (((x % ((2u & 7u) + 1u)) | (2147483647u - x)) & 31u));
  unsigned b = (((a * 1u) << (a & 31u)) ^ ((y ^ z) / (((x / ((15u & 7u) + 1u)) & 7u) + 1u)));
  unsigned r = (31u ^ ((2u / ((y & 7u) + 1u)) & (a - 1u)));
  if (((1u * (r & a)) >= 2u)) {
    r = b;
  } else {
    r = x;
  }
  return r;
}
