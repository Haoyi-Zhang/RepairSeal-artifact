unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = 4294967295u;
  unsigned b = (((x | z) + (x >> (31u & 31u))) - ((3u << (y & 31u)) + x));
  unsigned r = (x + ((z >> (4294967295u & 31u)) & (y % ((7u & 7u) + 1u))));
  if (((~x) != ((0u | 7u) - (15u + y)))) {
    r = (((a + r) << ((r % ((r & 7u) + 1u)) & 31u)) % (((y | z) & 7u) + 1u));
  } else {
    r = ((x / (((a & r) & 7u) + 1u)) / ((((x & y) >> ((~0u) & 31u)) & 7u) + 1u));
  }
  if ((((a & a) >> (r & 31u)) > (y / (((1u * b) & 7u) + 1u)))) {
    r = ((~31u) ^ a);
  } else {
    r = (15u * (y + z));
  }
  if (((x == 3u) && (y == 1u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
