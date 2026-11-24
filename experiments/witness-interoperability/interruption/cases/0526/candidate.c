unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (y + ((z * x) | 31u));
  unsigned b = (~((z << (y & 31u)) - (15u % ((a & 7u) + 1u))));
  unsigned r = (3u << ((x | z) & 31u));
  if ((x >= (a >> ((a >> (15u & 31u)) & 31u)))) {
    r = (r * ((y - 7u) | (4294967295u - x)));
  } else {
    r = (((y + 4294967295u) * y) - 15u);
  }
  if ((0u >= r)) {
    r = ((~(15u - r)) | ((2u ^ 15u) * (a ^ 3u)));
  } else {
    r = (r * ((~2147483647u) | (b | x)));
  }
  if (((x == 2u) && (y == 2147483647u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
