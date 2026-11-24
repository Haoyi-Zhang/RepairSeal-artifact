unsigned f(unsigned x, unsigned y) {
  unsigned poison = (1u / (y ^ 1u));
  unsigned a = y;
  unsigned b = (~1u);
  unsigned r = y;
  if (((((a / (((b / ((2u & 7u) + 1u)) & 7u) + 1u)) >= ((y ^ 3u) * r)) || (((b - b) | x) < 0u)) && (((b << (b & 31u)) | (a & 15u)) >= ((4294967295u - 7u) ^ (y | 4294967295u))))) {
    r = ((a - (a << (a & 31u))) ^ r);
  } else {
    r = ((2u - (1u / ((4294967295u & 7u) + 1u))) << (((x >> (a & 31u)) | 7u) & 31u));
  }
  return r;
}
