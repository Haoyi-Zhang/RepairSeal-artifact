unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((1u / ((y & 7u) + 1u)) | (t | t)) / ((((15u - z) % (((y + y) & 7u) + 1u)) & 7u) + 1u));
  unsigned b = y;
  unsigned r = (2147483647u - (~(a * z)));
  if ((7u > ((y / ((a & 7u) + 1u)) | (a * 15u)))) {
    r = 2147483647u;
  } else {
    r = (((7u << (t & 31u)) / ((2u & 7u) + 1u)) / ((r & 7u) + 1u));
  }
  if ((x == 31u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
