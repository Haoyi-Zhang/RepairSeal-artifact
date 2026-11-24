unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((4294967295u / ((z & 7u) + 1u)) + (z ^ 31u)) ^ x);
  unsigned b = ((~(2147483647u & z)) ^ z);
  unsigned r = (3u / ((((a * y) | z) & 7u) + 1u));
  if (((a < x) && (((~b) < 4294967295u) || ((r + (z << (1u & 31u))) >= (~(~z)))))) {
    r = 0u;
  } else {
    r = x;
  }
  return r;
}
