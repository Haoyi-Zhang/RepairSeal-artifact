unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (7u | x);
  unsigned b = ((x * (~4294967295u)) - (z >> (x & 31u)));
  unsigned r = (((z << (a & 31u)) / (((a & x) & 7u) + 1u)) << (((x >> (2u & 31u)) | y) & 31u));
  if ((a == (~z))) {
    r = (y | ((~3u) >> ((2147483647u & y) & 31u)));
  } else {
    r = (((x * x) | (x & y)) >> ((3u - r) & 31u));
  }
  if (((x >= (b - (y - r))) || (!(2u != 2147483647u)))) {
    r = (((z >> (y & 31u)) - (~x)) << (((a >> (r & 31u)) % (((2u | r) & 7u) + 1u)) & 31u));
  } else {
    r = (4294967295u % ((((x | x) ^ 15u) & 7u) + 1u));
  }
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
