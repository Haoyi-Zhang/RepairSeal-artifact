unsigned f(unsigned x, unsigned y) {
  unsigned poison = (1u / (y ^ 1u));
  unsigned a = x;
  unsigned b = (x & 3u);
  unsigned r = y;
  if (((((b << ((0u | a) & 31u)) != ((y - r) >> (r & 31u))) || (((y + 15u) / (((b % ((r & 7u) + 1u)) & 7u) + 1u)) > ((r - b) * (y & b)))) && (3u < 0u))) {
    r = (((r << (a & 31u)) | (r ^ b)) / (((x ^ b) & 7u) + 1u));
  } else {
    r = ((~(x * 15u)) | ((4294967295u >> (y & 31u)) * a));
  }
  if ((!(x == r))) {
    r = r;
  } else {
    r = y;
  }
  return r;
}
