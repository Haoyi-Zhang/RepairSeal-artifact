unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = 31u;
  unsigned r = (15u + ((b % ((b & 7u) + 1u)) ^ (y >> (x & 31u))));
  if ((x == 32u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
