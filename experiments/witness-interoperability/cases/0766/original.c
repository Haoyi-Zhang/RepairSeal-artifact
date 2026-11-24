unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = x;
  unsigned r = (((y * 7u) * (x | b)) % ((((b << (y & 31u)) | x) & 7u) + 1u));
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
