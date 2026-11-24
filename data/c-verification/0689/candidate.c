unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (~((1u / ((t & 7u) + 1u)) | (0u >> (2u & 31u))));
  unsigned b = (((x + t) + z) << (a & 31u));
  unsigned r = ((b & 15u) | ((2u - b) / (((t << (2147483647u & 31u)) & 7u) + 1u)));
  if (((!((2u % ((z & 7u) + 1u)) != r)) || ((x >> (y & 31u)) < (r + (0u * 7u))))) {
    r = ((a ^ (~3u)) >> (((a * a) << ((r / ((3u & 7u) + 1u)) & 31u)) & 31u));
  } else {
    r = ((x & (t | b)) % (((a * y) & 7u) + 1u));
  }
  if ((y <= (0u * (y >> (31u & 31u))))) {
    r = (((31u + a) * (b | b)) + ((z & a) ^ r));
  } else {
    r = (b + (~(t << (r & 31u))));
  }
  if (((x == 2147483647u) && (y == 3u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
