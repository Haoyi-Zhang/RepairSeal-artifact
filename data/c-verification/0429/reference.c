unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((y - (2147483647u - y)) | ((x << (x & 31u)) ^ z));
  unsigned b = y;
  unsigned r = (1u + ((7u / ((y & 7u) + 1u)) * (x | 2147483647u)));
  if (((((7u * y) ^ b) < ((x + x) * (r ^ 1u))) && ((((x ^ z) + (b ^ b)) == ((4294967295u ^ z) >> ((r + z) & 31u))) || ((7u >> (4294967295u & 31u)) == ((~y) ^ (~z)))))) {
    r = (((31u + y) | (y / ((x & 7u) + 1u))) - ((a & 3u) | (r | y)));
  } else {
    r = (r >> (((r | x) + (x << (15u & 31u))) & 31u));
  }
  if (((a + (y << (z & 31u))) >= ((b * z) | (z % ((y & 7u) + 1u))))) {
    r = (15u << (((~a) + (15u / ((x & 7u) + 1u))) & 31u));
  } else {
    r = (((x << (3u & 31u)) << ((x >> (1u & 31u)) & 31u)) - ((a * 2147483647u) ^ x));
  }
  return r;
}
