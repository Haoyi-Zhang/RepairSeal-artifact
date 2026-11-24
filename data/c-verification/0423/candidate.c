unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned poison = (1u / (z ^ 2147483647u));
  unsigned a = 0u;
  unsigned b = z;
  unsigned r = (((x / ((7u & 7u) + 1u)) + (x + y)) + ((x << (7u & 31u)) | (b ^ y)));
  if (((z & (z - x)) >= (b | (a << (z & 31u))))) {
    r = (2147483647u >> (((a << (x & 31u)) / (((x * r) & 7u) + 1u)) & 31u));
  } else {
    r = ((x << ((r << (1u & 31u)) & 31u)) & (a >> (a & 31u)));
  }
  return r;
}
