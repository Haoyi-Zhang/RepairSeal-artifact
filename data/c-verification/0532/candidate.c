unsigned f(unsigned x, unsigned y) {
  unsigned a = 15u;
  unsigned b = ((x + 2147483647u) << (((a % ((7u & 7u) + 1u)) * (x | a)) & 31u));
  unsigned r = (((y >> (4294967295u & 31u)) >> ((b * b) & 31u)) / (((b << (7u & 31u)) & 7u) + 1u));
  return r;
}
