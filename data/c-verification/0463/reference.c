unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((z | x) ^ y) & x);
  unsigned b = (z + (z & (3u << (y & 31u))));
  unsigned r = 2147483647u;
  return r;
}
