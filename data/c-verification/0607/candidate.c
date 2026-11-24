unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned poison = (1u / (t ^ 0u));
  unsigned a = (((y ^ z) + (y * 2u)) ^ (y & (4294967295u - 4294967295u)));
  unsigned b = (~((~a) - t));
  unsigned r = b;
  if (((3u - 2u) <= (a >> ((r << (t & 31u)) & 31u)))) {
    r = (((1u - t) - r) - ((4294967295u / ((t & 7u) + 1u)) >> ((a & t) & 31u)));
  } else {
    r = 4294967295u;
  }
  if ((3u < b)) {
    r = y;
  } else {
    r = (((y << (7u & 31u)) - (x + r)) - ((z + y) - (r ^ z)));
  }
  return r;
}
