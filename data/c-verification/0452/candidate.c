unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = ((1u + (7u | 15u)) * y);
  unsigned r = (((y * x) << ((x / ((7u & 7u) + 1u)) & 31u)) | ((a & 2147483647u) + (31u << (b & 31u))));
  if ((a <= (a << (b & 31u)))) {
    r = x;
  } else {
    r = (((31u % ((r & 7u) + 1u)) / ((0u & 7u) + 1u)) << (((~y) ^ b) & 31u));
  }
  if (((b >= ((x / ((r & 7u) + 1u)) + (1u | x))) || ((b < ((y % ((x & 7u) + 1u)) * (b ^ y))) && (((x ^ 31u) | y) >= ((r ^ y) & 3u))))) {
    r = (y - ((~y) % (((~r) & 7u) + 1u)));
  } else {
    r = (15u & (~(a * 3u)));
  }
  return r;
}
