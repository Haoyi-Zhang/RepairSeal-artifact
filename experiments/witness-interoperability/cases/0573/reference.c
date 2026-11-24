unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (~((3u / ((t & 7u) + 1u)) >> ((0u % ((t & 7u) + 1u)) & 31u)));
  unsigned b = ((y - (y / ((x & 7u) + 1u))) - (z * 2u));
  unsigned r = (4294967295u << (z & 31u));
  if ((!(((b * r) % (((y & a) & 7u) + 1u)) >= (y + r)))) {
    r = (((b % ((y & 7u) + 1u)) ^ (y + 3u)) + (4294967295u ^ (2147483647u + y)));
  } else {
    r = (x * z);
  }
  if ((a != ((z * 15u) | (~y)))) {
    r = 31u;
  } else {
    r = (b & ((t & r) ^ (~r)));
  }
  return r;
}
