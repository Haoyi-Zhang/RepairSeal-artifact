unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((y - y) << ((z - 0u) & 31u)) * (0u / (((z >> (4294967295u & 31u)) & 7u) + 1u)));
  unsigned b = 4294967295u;
  unsigned r = b;
  if ((b == ((r << (y & 31u)) | r))) {
    r = y;
  } else {
    r = (((z << (r & 31u)) * y) * ((31u >> (15u & 31u)) / (((a ^ y) & 7u) + 1u)));
  }
  if ((x == 2147483647u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
