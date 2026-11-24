unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (3u % (((15u + 7u) & 7u) + 1u));
  unsigned b = x;
  unsigned r = z;
  if (((r - (7u * x)) != t)) {
    r = (~((x + a) ^ 3u));
  } else {
    r = ((3u - (2u ^ a)) * 1u);
  }
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
