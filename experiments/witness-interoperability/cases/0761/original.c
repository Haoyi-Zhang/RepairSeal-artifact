unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((x << (z & 31u)) % ((t & 7u) + 1u)) << ((~x) & 31u));
  unsigned b = (a & 15u);
  unsigned r = a;
  if ((!((x <= ((1u + y) | 0u)) || ((~0u) != ((x * r) << ((t & x) & 31u)))))) {
    r = (((1u % ((r & 7u) + 1u)) & z) & y);
  } else {
    r = ((31u << (4294967295u & 31u)) >> (((b - y) - (~4294967295u)) & 31u));
  }
  if ((((a == (2147483647u / (((b >> (t & 31u)) & 7u) + 1u))) && (a != ((b * 0u) ^ (~x)))) || (t >= (y + (t & 2u))))) {
    r = (((z % ((y & 7u) + 1u)) * (~r)) | b);
  } else {
    r = 3u;
  }
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
