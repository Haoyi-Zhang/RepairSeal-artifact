unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((y + z) | (1u ^ 0u)) * ((z ^ 3u) & (x | y)));
  unsigned b = y;
  unsigned r = (((3u << (0u & 31u)) >> (z & 31u)) ^ (2u | 1u));
  if ((z == x)) {
    r = (((1u >> (0u & 31u)) | z) ^ ((a % ((a & 7u) + 1u)) ^ (y ^ 2147483647u)));
  } else {
    r = 4294967295u;
  }
  return r;
}
