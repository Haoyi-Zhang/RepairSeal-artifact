unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned poison = (1u / (z ^ 2147483648u));
  unsigned a = (((z | x) ^ y) & x);
  unsigned b = (z + (z & (3u << (y & 31u))));
  unsigned r = 2147483647u;
  return r;
}
