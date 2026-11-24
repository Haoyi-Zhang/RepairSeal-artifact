unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((z | x) << ((1u | y) & 31u)) / ((x & 7u) + 1u));
  unsigned b = (3u + 2u);
  unsigned r = x;
  if ((((r / ((7u & 7u) + 1u)) | (~b)) == ((31u * x) << ((b - x) & 31u)))) {
    r = (((2147483647u & b) - (b - z)) | y);
  } else {
    r = z;
  }
  if (((((1u & r) ^ (z ^ z)) == ((x % ((x & 7u) + 1u)) | y)) && ((y & b) != (b >> ((2147483647u % ((z & 7u) + 1u)) & 31u))))) {
    r = r;
  } else {
    r = 7u;
  }
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
