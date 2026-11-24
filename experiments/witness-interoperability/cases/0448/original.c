unsigned f(unsigned x, unsigned y) {
  unsigned a = (2147483647u * y);
  unsigned b = x;
  unsigned r = (((~y) - (y / ((a & 7u) + 1u))) - (x & (a % ((x & 7u) + 1u))));
  if (((((b << (x & 31u)) % (((a + y) & 7u) + 1u)) <= (x & 4294967295u)) || (b == ((2147483647u >> (1u & 31u)) + (b % ((r & 7u) + 1u)))))) {
    r = x;
  } else {
    r = (((~2u) / (((b - y) & 7u) + 1u)) | ((r << (x & 31u)) ^ (~r)));
  }
  if ((0u < ((b - r) / (((x & r) & 7u) + 1u)))) {
    r = b;
  } else {
    r = 3u;
  }
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
