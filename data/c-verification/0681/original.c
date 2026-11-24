unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((3u >> ((31u - y) & 31u)) << ((~x) & 31u));
  unsigned b = (31u | a);
  unsigned r = (((x | a) >> ((y / ((z & 7u) + 1u)) & 31u)) - 2u);
  if ((!(((r % ((z & 7u) + 1u)) << ((z - x) & 31u)) == (0u / (((~z) & 7u) + 1u))))) {
    r = (((y / ((1u & 7u) + 1u)) | (b & 15u)) % ((y & 7u) + 1u));
  } else {
    r = b;
  }
  if (((7u >= ((7u << (3u & 31u)) - (b + b))) || ((~(r >> (a & 31u))) == (b % (((z * y) & 7u) + 1u))))) {
    r = 3u;
  } else {
    r = a;
  }
  if ((x == 2147483647u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
