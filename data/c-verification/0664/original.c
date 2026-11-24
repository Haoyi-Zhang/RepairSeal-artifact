unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((z - (1u * z)) & (t - t));
  unsigned b = (((a % ((1u & 7u) + 1u)) | 15u) % (((x | (15u % ((31u & 7u) + 1u))) & 7u) + 1u));
  unsigned r = (((t ^ x) | (t / ((2u & 7u) + 1u))) & 1u);
  if (((((z * a) ^ (t & 4294967295u)) < ((~31u) + (31u * y))) || (((2u ^ (r / ((7u & 7u) + 1u))) > b) && ((~31u) >= ((31u | 15u) - (t * 3u)))))) {
    r = (2147483647u ^ a);
  } else {
    r = (((2u - x) ^ (y + 3u)) >> (((x - b) >> (r & 31u)) & 31u));
  }
  if ((x == 31u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
