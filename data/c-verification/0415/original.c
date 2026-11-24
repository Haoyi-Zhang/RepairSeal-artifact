unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((x - (y + z)) - (x / (((x ^ x) & 7u) + 1u)));
  unsigned b = (0u - ((t % ((x & 7u) + 1u)) - 7u));
  unsigned r = (((2147483647u | a) % ((0u & 7u) + 1u)) % (((y ^ (31u & z)) & 7u) + 1u));
  if (((((2u & t) >> ((r << (y & 31u)) & 31u)) >= ((0u | a) & 2u)) || (b > ((a % ((x & 7u) + 1u)) << ((4294967295u * a) & 31u))))) {
    r = (((z | b) << (3u & 31u)) * ((r + y) >> (a & 31u)));
  } else {
    r = (((b >> (r & 31u)) % (((4294967295u >> (t & 31u)) & 7u) + 1u)) >> ((z & y) & 31u));
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
