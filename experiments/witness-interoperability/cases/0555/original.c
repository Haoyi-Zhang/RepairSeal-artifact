unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = y;
  unsigned b = (((31u ^ 7u) << ((y << (a & 31u)) & 31u)) | ((x / ((x & 7u) + 1u)) * (x << (x & 31u))));
  unsigned r = a;
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
