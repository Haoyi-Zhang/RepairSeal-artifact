unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((x | z) ^ (y % ((y & 7u) + 1u))) * ((~y) << ((y & x) & 31u)));
  unsigned b = (((a << (z & 31u)) | a) + (x ^ z));
  unsigned r = (((~a) & (a - b)) ^ ((~x) * 15u));
  if (((x == 2147483648u) && (y == 4294967295u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
