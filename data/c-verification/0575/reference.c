unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((x << (31u & 31u)) / (((y * 1u) & 7u) + 1u)) - z);
  unsigned b = (0u + 2147483647u);
  unsigned r = (((y * y) / (((x * a) & 7u) + 1u)) - ((y / ((x & 7u) + 1u)) >> (3u & 31u)));
  if ((((r > ((z - 0u) & (b >> (y & 31u)))) && ((a ^ (2147483647u | 31u)) == a)) && (((r ^ z) / (((a | a) & 7u) + 1u)) != (y % (((z << (y & 31u)) & 7u) + 1u))))) {
    r = (((a >> (15u & 31u)) * y) * ((4294967295u | z) ^ (y % ((a & 7u) + 1u))));
  } else {
    r = ((a ^ x) | ((~z) + (x & r)));
  }
  return r;
}
