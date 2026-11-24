unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = 31u;
  unsigned b = (((15u * a) * (a & z)) / (((31u - (31u | z)) & 7u) + 1u));
  unsigned r = a;
  if ((b == (a ^ (a ^ 0u)))) {
    r = (((z + 15u) + (y << (2147483647u & 31u))) >> (((r >> (a & 31u)) & (r - 2147483647u)) & 31u));
  } else {
    r = (((r | x) ^ (4294967295u * y)) >> (((3u * 7u) * a) & 31u));
  }
  return r;
}
