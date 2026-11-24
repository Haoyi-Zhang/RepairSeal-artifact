unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((15u / (((x | z) & 7u) + 1u)) >> (y & 31u));
  unsigned b = (y - (y | (1u * x)));
  unsigned r = (y >> (((b >> (z & 31u)) << ((y & y) & 31u)) & 31u));
  if (((y > r) || (3u >= (4294967295u + (b | x))))) {
    r = x;
  } else {
    r = a;
  }
  if (((a > ((31u / ((x & 7u) + 1u)) ^ (z >> (31u & 31u)))) || (((~z) < y) && (((15u - r) - (2147483647u | z)) >= ((b >> (z & 31u)) & (~b)))))) {
    r = y;
  } else {
    r = (((r % ((z & 7u) + 1u)) / ((x & 7u) + 1u)) | (x & (z ^ 15u)));
  }
  return r;
}
