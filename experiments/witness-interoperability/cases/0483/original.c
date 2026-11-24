unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((~(15u % ((x & 7u) + 1u))) << (3u & 31u));
  unsigned b = (~((z / ((x & 7u) + 1u)) | (7u << (2147483647u & 31u))));
  unsigned r = (((z - 2u) + (2u * 2u)) & ((a + b) + z));
  if ((y >= ((b & b) * (b & 3u)))) {
    r = r;
  } else {
    r = ((15u - r) ^ ((y << (b & 31u)) + (x + a)));
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
