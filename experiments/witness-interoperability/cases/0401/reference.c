unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = 3u;
  unsigned b = 2u;
  unsigned r = (((z / ((b & 7u) + 1u)) % ((0u & 7u) + 1u)) & (z + (b & x)));
  if (((2u | x) < ((x << (x & 31u)) << ((y / ((a & 7u) + 1u)) & 31u)))) {
    r = b;
  } else {
    r = (a * ((r << (z & 31u)) ^ (7u & t)));
  }
  if ((((31u & x) / (((2147483647u % ((t & 7u) + 1u)) & 7u) + 1u)) > ((t % ((a & 7u) + 1u)) << (z & 31u)))) {
    r = 2u;
  } else {
    r = 0u;
  }
  return r;
}
