unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((15u | (x / ((4294967295u & 7u) + 1u))) & x);
  unsigned b = (((1u | a) << (y & 31u)) - (3u * (a % ((z & 7u) + 1u))));
  unsigned r = (((x % ((7u & 7u) + 1u)) | y) ^ (2u * (a & z)));
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
