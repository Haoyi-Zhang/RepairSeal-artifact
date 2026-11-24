unsigned f(unsigned x, unsigned y) {
  unsigned poison = (1u / (y ^ 2u));
  unsigned a = (((x + x) & 2u) + ((y >> (y & 31u)) + (31u & x)));
  unsigned b = ((a | (y + y)) >> (a & 31u));
  unsigned r = (~(y * (1u + y)));
  return r;
}
