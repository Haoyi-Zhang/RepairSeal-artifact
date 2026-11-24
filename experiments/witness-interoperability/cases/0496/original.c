unsigned f(unsigned x, unsigned y) {
  unsigned a = (((y * 4294967295u) << ((x & x) & 31u)) % ((7u & 7u) + 1u));
  unsigned b = ((y / (((x >> (x & 31u)) & 7u) + 1u)) | (y >> ((~a) & 31u)));
  unsigned r = ((b - y) + (15u ^ (b - b)));
  if ((a <= ((y % ((0u & 7u) + 1u)) << (0u & 31u)))) {
    r = x;
  } else {
    r = (((a % ((y & 7u) + 1u)) * r) / ((((r - y) % (((0u << (a & 31u)) & 7u) + 1u)) & 7u) + 1u));
  }
  if ((!((a / (((a + x) & 7u) + 1u)) > 4294967295u))) {
    r = (~4294967295u);
  } else {
    r = (~(a / ((a & 7u) + 1u)));
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
