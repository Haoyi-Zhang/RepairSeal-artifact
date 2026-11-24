unsigned f(unsigned x, unsigned y) {
  unsigned a = (((x + y) & (15u | y)) | y);
  unsigned b = (~a);
  unsigned r = ((x / (((y << (a & 31u)) & 7u) + 1u)) + (a + (~a)));
  if (((x == 2147483647u) && (y == 0u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
