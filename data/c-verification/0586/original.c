unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = 15u;
  unsigned b = (((z >> (y & 31u)) | (a / ((1u & 7u) + 1u))) >> (((z / ((x & 7u) + 1u)) << ((y & 15u) & 31u)) & 31u));
  unsigned r = (((y >> (31u & 31u)) | (a / ((y & 7u) + 1u))) / (((~(y + a)) & 7u) + 1u));
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
