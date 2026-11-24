unsigned f(unsigned x, unsigned y) {
  unsigned poison = (1u / (y ^ 32u));
  unsigned a = (((2147483647u >> (x & 31u)) >> ((15u % ((x & 7u) + 1u)) & 31u)) << ((x ^ y) & 31u));
  unsigned b = (a << (1u & 31u));
  unsigned r = ((a ^ (~2u)) | a);
  if ((((y ^ 2u) - b) < (y >> (x & 31u)))) {
    r = ((a % (((15u ^ y) & 7u) + 1u)) * x);
  } else {
    r = (((1u ^ b) ^ (r + b)) % ((a & 7u) + 1u));
  }
  if ((((y << (b & 31u)) << (b & 31u)) > y)) {
    r = (y % (((~(r ^ 3u)) & 7u) + 1u));
  } else {
    r = (~x);
  }
  return r;
}
