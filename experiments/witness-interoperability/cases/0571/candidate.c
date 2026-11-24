unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned poison = (1u / (z ^ 2147483648u));
  unsigned a = (((y >> (z & 31u)) & 2147483647u) | (31u - (x >> (x & 31u))));
  unsigned b = (((2u & 2u) >> ((z - y) & 31u)) / ((((x % ((x & 7u) + 1u)) | (0u * 0u)) & 7u) + 1u));
  unsigned r = a;
  return r;
}
