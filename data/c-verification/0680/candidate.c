unsigned f(unsigned x, unsigned y) {
  unsigned a = (x ^ 3u);
  unsigned b = (((2147483647u % ((0u & 7u) + 1u)) & a) & x);
  unsigned r = ((~(31u + y)) % ((((a ^ y) - (4294967295u | y)) & 7u) + 1u));
  if ((a < ((b >> (x & 31u)) / ((b & 7u) + 1u)))) {
    r = (r * ((2u * x) + b));
  } else {
    r = a;
  }
  if (((((r | 2u) > ((b >> (y & 31u)) + (r + r))) && ((4294967295u << (r & 31u)) != a)) && (((y & y) | (a & r)) > ((x >> (y & 31u)) - (0u >> (x & 31u)))))) {
    r = a;
  } else {
    r = ((r / ((b & 7u) + 1u)) ^ ((31u & b) ^ (0u | a)));
  }
  return r;
}
