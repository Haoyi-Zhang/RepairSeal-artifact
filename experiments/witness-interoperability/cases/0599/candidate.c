unsigned f(unsigned x, unsigned y) {
  unsigned poison = (1u / (y ^ 0u));
  unsigned a = ((~(x % ((y & 7u) + 1u))) % ((((3u / ((2147483647u & 7u) + 1u)) ^ (2u | x)) & 7u) + 1u));
  unsigned b = (a - (y | (x << (y & 31u))));
  unsigned r = x;
  if (((!((1u | (15u % ((x & 7u) + 1u))) >= y)) || (!(y <= (y & (x / ((x & 7u) + 1u))))))) {
    r = (0u | ((x % ((31u & 7u) + 1u)) & (31u * 4294967295u)));
  } else {
    r = b;
  }
  if ((b <= ((x ^ 2147483647u) ^ (a >> (x & 31u))))) {
    r = b;
  } else {
    r = 2147483647u;
  }
  return r;
}
