unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = y;
  unsigned b = ((~(z >> (t & 31u))) << (((2147483647u ^ y) / (((z - z) & 7u) + 1u)) & 31u));
  unsigned r = (((x - z) - (3u | 3u)) << (((1u / ((z & 7u) + 1u)) & y) & 31u));
  if ((!((a != ((2u & 0u) % (((7u & x) & 7u) + 1u))) && (x == ((y * 4294967295u) / (((t % ((4294967295u & 7u) + 1u)) & 7u) + 1u)))))) {
    r = (15u >> (x & 31u));
  } else {
    r = 2u;
  }
  if (((x == 2147483648u) && (y == 2147483648u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
