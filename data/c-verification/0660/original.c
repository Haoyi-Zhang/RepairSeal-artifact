unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (~((4294967295u + x) + (0u + 7u)));
  unsigned b = (((x - z) / (((15u - z) & 7u) + 1u)) | ((15u ^ 31u) / ((31u & 7u) + 1u)));
  unsigned r = ((x << ((x - x) & 31u)) / ((((b / ((a & 7u) + 1u)) & (z + y)) & 7u) + 1u));
  if ((x == 32u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
