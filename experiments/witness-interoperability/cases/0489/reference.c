unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((x | z) ^ (y % ((y & 7u) + 1u))) * ((~y) << ((y & x) & 31u)));
  unsigned b = (((a << (z & 31u)) | a) + (x ^ z));
  unsigned r = (((~a) & (a - b)) ^ ((~x) * 15u));
  return r;
}
