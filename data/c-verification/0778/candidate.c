unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((x >> (2147483647u & 31u)) << ((~z) & 31u));
  unsigned b = 4294967295u;
  unsigned r = (2u & x);
  if (((3u / (((~a) & 7u) + 1u)) > (2147483647u / (((b << (y & 31u)) & 7u) + 1u)))) {
    r = (((~2147483647u) / (((r - x) & 7u) + 1u)) >> (((z >> (a & 31u)) | (31u >> (a & 31u))) & 31u));
  } else {
    r = (r * r);
  }
  if (((x == 2147483647u) && (y == 1u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
