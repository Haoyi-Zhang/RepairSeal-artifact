unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = x;
  unsigned r = (((y * 7u) * (x | b)) % ((((b << (y & 31u)) | x) & 7u) + 1u));
  if (((x == 2147483647u) && (y == 3u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
