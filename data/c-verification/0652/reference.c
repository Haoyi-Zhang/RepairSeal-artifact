unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = 7u;
  unsigned b = ((~a) >> (((y % ((x & 7u) + 1u)) % (((y * y) & 7u) + 1u)) & 31u));
  unsigned r = (((x >> (a & 31u)) / (((~y) & 7u) + 1u)) | (b / (((a - z) & 7u) + 1u)));
  if (((x < (z | x)) || ((((~b) ^ (b << (z & 31u))) == 15u) && ((a % (((r >> (r & 31u)) & 7u) + 1u)) < y)))) {
    r = 31u;
  } else {
    r = a;
  }
  if ((b < b)) {
    r = ((3u - 2147483647u) / ((r & 7u) + 1u));
  } else {
    r = ((a & x) / ((r & 7u) + 1u));
  }
  return r;
}
