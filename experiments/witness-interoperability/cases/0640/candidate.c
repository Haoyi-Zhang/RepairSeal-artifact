unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((~(31u % ((z & 7u) + 1u))) >> (((x | y) << ((3u % ((y & 7u) + 1u)) & 31u)) & 31u));
  unsigned b = ((a - (y - 31u)) >> ((0u << ((y / ((4294967295u & 7u) + 1u)) & 31u)) & 31u));
  unsigned r = ((z + x) / (((~1u) & 7u) + 1u));
  if ((x == (a / (((~2u) & 7u) + 1u)))) {
    r = (((b + r) * 2147483647u) >> ((~(y >> (b & 31u))) & 31u));
  } else {
    r = (((y - b) << ((z ^ b) & 31u)) >> (((b >> (b & 31u)) | (x + b)) & 31u));
  }
  if ((!(!((a ^ (z ^ 0u)) < (x << ((r & b) & 31u)))))) {
    r = ((~(31u ^ z)) + (0u >> ((1u / ((2147483647u & 7u) + 1u)) & 31u)));
  } else {
    r = (7u ^ (a | (b ^ x)));
  }
  return r;
}
