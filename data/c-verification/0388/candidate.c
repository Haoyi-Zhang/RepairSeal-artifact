unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = x;
  unsigned b = (~1u);
  unsigned r = ((4294967295u / ((2147483647u & 7u) + 1u)) & y);
  if ((((a % ((b & 7u) + 1u)) - (~2u)) == a)) {
    r = (((1u ^ x) - (y & b)) ^ 2u);
  } else {
    r = (((r | r) % (((4294967295u << (b & 31u)) & 7u) + 1u)) + ((b / ((z & 7u) + 1u)) ^ (15u - y)));
  }
  if ((x != (y ^ (a ^ y)))) {
    r = ((~z) | (r >> ((2147483647u ^ z) & 31u)));
  } else {
    r = (((b * z) << ((1u * z) & 31u)) - ((r >> (y & 31u)) + (z * x)));
  }
  return r;
}
