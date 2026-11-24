unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((~(x ^ 7u)) % (((t - (2147483647u >> (t & 31u))) & 7u) + 1u));
  unsigned b = z;
  unsigned r = (2147483647u - x);
  if ((((4294967295u << (y & 31u)) % ((a & 7u) + 1u)) < ((r % ((z & 7u) + 1u)) | (x ^ 3u)))) {
    r = 0u;
  } else {
    r = (x - (z >> ((0u >> (15u & 31u)) & 31u)));
  }
  if ((4294967295u >= r)) {
    r = a;
  } else {
    r = (((y >> (b & 31u)) % (((~t) & 7u) + 1u)) / ((t & 7u) + 1u));
  }
  return r;
}
