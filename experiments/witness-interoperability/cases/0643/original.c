unsigned f(unsigned x, unsigned y) {
  unsigned a = (((y * y) % (((15u | 0u) & 7u) + 1u)) | y);
  unsigned b = (2u >> ((7u ^ y) & 31u));
  unsigned r = (((~x) & (y >> (x & 31u))) % ((((y | y) % (((a << (a & 31u)) & 7u) + 1u)) & 7u) + 1u));
  if ((x == 2147483647u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
