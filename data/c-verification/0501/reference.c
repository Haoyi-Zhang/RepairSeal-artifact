unsigned f(unsigned x, unsigned y) {
  unsigned a = (((x + y) & (15u | y)) | y);
  unsigned b = (~a);
  unsigned r = ((x / (((y << (a & 31u)) & 7u) + 1u)) + (a + (~a)));
  return r;
}
