unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = 15u;
  unsigned b = (((a >> (0u & 31u)) ^ (x % ((x & 7u) + 1u))) | ((z * 0u) * (y % ((x & 7u) + 1u))));
  unsigned r = ((1u ^ 15u) & ((b / ((0u & 7u) + 1u)) + x));
  if ((((((7u << (y & 31u)) | 2147483647u) != ((1u ^ 7u) & (3u ^ 1u))) && (((z + 3u) / (((r >> (a & 31u)) & 7u) + 1u)) <= x)) && (((31u / ((b & 7u) + 1u)) << (4294967295u & 31u)) != ((1u >> (0u & 31u)) * (3u % ((r & 7u) + 1u)))))) {
    r = (b & ((y >> (z & 31u)) + (4294967295u | r)));
  } else {
    r = (z & (y | (x | a)));
  }
  if ((((y <= y) || (31u < a)) && (((b | a) != ((7u ^ 2u) << ((3u / ((b & 7u) + 1u)) & 31u))) && (((z & r) % (((y ^ 4294967295u) & 7u) + 1u)) <= ((a & r) - (x % ((r & 7u) + 1u))))))) {
    r = 3u;
  } else {
    r = (y | r);
  }
  return r;
}
