unsigned f(unsigned x, unsigned y) {
  unsigned a = (x - ((~15u) >> (y & 31u)));
  unsigned b = y;
  unsigned r = y;
  if ((((b & 31u) ^ a) >= (~b))) {
    r = b;
  } else {
    r = (x + (x % (((~x) & 7u) + 1u)));
  }
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
