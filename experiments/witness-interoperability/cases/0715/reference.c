unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = y;
  unsigned b = ((z & (31u & z)) | ((z << (z & 31u)) % (((0u & y) & 7u) + 1u)));
  unsigned r = 2u;
  if ((b != ((r & x) ^ (0u | 1u)))) {
    r = (((z * x) ^ (~y)) << ((~(y << (z & 31u))) & 31u));
  } else {
    r = a;
  }
  return r;
}
