unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned poison = (1u / (z ^ 2147483647u));
  unsigned a = ((x ^ (x % ((z & 7u) + 1u))) << (7u & 31u));
  unsigned b = (((z / ((x & 7u) + 1u)) * (4294967295u & 7u)) / ((((~a) % ((2u & 7u) + 1u)) & 7u) + 1u));
  unsigned r = ((~(a - z)) * (y - (1u & z)));
  if ((((a ^ 3u) ^ a) != (3u & (b % ((a & 7u) + 1u))))) {
    r = 31u;
  } else {
    r = b;
  }
  return r;
}
