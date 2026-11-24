unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (y / ((((~x) + (3u / ((z & 7u) + 1u))) & 7u) + 1u));
  unsigned b = (a * x);
  unsigned r = (~(~(2147483647u / ((b & 7u) + 1u))));
  if ((((b | 2u) << (r & 31u)) <= z)) {
    r = (b ^ (r - z));
  } else {
    r = (r / ((y & 7u) + 1u));
  }
  return r;
}
