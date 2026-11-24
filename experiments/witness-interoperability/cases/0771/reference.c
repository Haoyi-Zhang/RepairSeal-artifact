unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((x / ((z & 7u) + 1u)) * z) >> (y & 31u));
  unsigned b = z;
  unsigned r = a;
  if ((((3u % ((r & 7u) + 1u)) & r) == (~(z / ((z & 7u) + 1u))))) {
    r = (((15u & y) ^ (b << (b & 31u))) * ((x << (3u & 31u)) | (x % ((z & 7u) + 1u))));
  } else {
    r = (((~b) / ((r & 7u) + 1u)) | ((z / ((2u & 7u) + 1u)) << (31u & 31u)));
  }
  if ((((x * b) | (~r)) <= a)) {
    r = (((2147483647u >> (x & 31u)) / ((y & 7u) + 1u)) << ((2u << (a & 31u)) & 31u));
  } else {
    r = (~1u);
  }
  return r;
}
