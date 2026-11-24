unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((~(31u >> (15u & 31u))) - y);
  unsigned b = (y | (z % (((a * 7u) & 7u) + 1u)));
  unsigned r = (((y >> (t & 31u)) | t) / (((y % (((y * t) & 7u) + 1u)) & 7u) + 1u));
  if (((x == 1u) && (y == 4294967295u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
