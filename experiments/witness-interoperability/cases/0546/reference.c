unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (x >> (((x * t) + x) & 31u));
  unsigned b = (z * a);
  unsigned r = (((t & 1u) >> (15u & 31u)) << (((b + b) / (((a ^ y) & 7u) + 1u)) & 31u));
  if ((3u > (7u & 7u))) {
    r = ((~(b & b)) | t);
  } else {
    r = (r * ((t - x) >> (0u & 31u)));
  }
  return r;
}
