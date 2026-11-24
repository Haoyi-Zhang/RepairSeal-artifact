unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = 15u;
  unsigned r = x;
  if (((r >> ((y ^ y) & 31u)) == ((a ^ x) ^ (7u << (2147483647u & 31u))))) {
    r = ((4294967295u | r) * ((x / ((y & 7u) + 1u)) - (x % ((y & 7u) + 1u))));
  } else {
    r = a;
  }
  if ((((15u + y) | 7u) > ((4294967295u | a) % (((~b) & 7u) + 1u)))) {
    r = (((x << (2147483647u & 31u)) >> ((~x) & 31u)) + (~(2u / ((a & 7u) + 1u))));
  } else {
    r = (((0u % ((b & 7u) + 1u)) ^ (x ^ 31u)) >> ((3u - (0u * x)) & 31u));
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
