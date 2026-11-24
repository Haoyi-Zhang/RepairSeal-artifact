unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = 2u;
  unsigned b = ((3u & y) % ((((a >> (2u & 31u)) | a) & 7u) + 1u));
  unsigned r = (((~x) * x) << ((a + (a << (1u & 31u))) & 31u));
  if (((x == 1u) && (y == 1u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
