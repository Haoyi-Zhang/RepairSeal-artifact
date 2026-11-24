unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned poison = (1u / (z ^ 31u));
  unsigned a = ((15u | (x / ((4294967295u & 7u) + 1u))) & x);
  unsigned b = (((1u | a) << (y & 31u)) - (3u * (a % ((z & 7u) + 1u))));
  unsigned r = (((x % ((7u & 7u) + 1u)) | y) ^ (2u * (a & z)));
  return r;
}
