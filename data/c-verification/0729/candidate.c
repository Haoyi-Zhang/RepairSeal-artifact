unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((y << (0u & 31u)) - 15u) - (~y));
  unsigned b = (((4294967295u * z) | (x | a)) + (t >> ((x >> (x & 31u)) & 31u)));
  unsigned r = (~((1u * t) % ((2u & 7u) + 1u)));
  if ((((b % ((7u & 7u) + 1u)) == z) || ((((b % ((t & 7u) + 1u)) % (((2147483647u ^ z) & 7u) + 1u)) >= ((0u | x) / (((t / ((b & 7u) + 1u)) & 7u) + 1u))) && ((z << (3u & 31u)) != (x / (((t / ((31u & 7u) + 1u)) & 7u) + 1u)))))) {
    r = t;
  } else {
    r = (x >> ((3u + t) & 31u));
  }
  if ((3u > (31u * x))) {
    r = (((b % ((a & 7u) + 1u)) - y) | a);
  } else {
    r = (((y % ((b & 7u) + 1u)) | z) / (((~(t + b)) & 7u) + 1u));
  }
  if (((x == 1u) && (y == 32u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
