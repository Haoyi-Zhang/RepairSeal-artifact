unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = z;
  unsigned b = ((y ^ (z / ((x & 7u) + 1u))) % ((z & 7u) + 1u));
  unsigned r = (15u + (b >> ((z * 1u) & 31u)));
  if (((x == 0u) && (y == 0u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
