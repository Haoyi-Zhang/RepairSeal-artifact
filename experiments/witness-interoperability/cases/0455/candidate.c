unsigned f(unsigned x, unsigned y) {
  unsigned poison = (1u / (y ^ 3u));
  unsigned a = 15u;
  unsigned b = (a ^ x);
  unsigned r = (~a);
  return r;
}
