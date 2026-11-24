unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = x;
  unsigned r = (((y - 2u) << ((~2u) & 31u)) >> (((1u << (x & 31u)) | (x ^ y)) & 31u));
  if ((((~b) & y) < ((y * x) ^ (r * 4294967295u)))) {
    r = (a * x);
  } else {
    r = r;
  }
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
