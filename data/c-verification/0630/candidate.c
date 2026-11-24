unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (t << (y & 31u));
  unsigned b = (((~2147483647u) << ((z | t) & 31u)) | x);
  unsigned r = (y * (4294967295u ^ b));
  if (((b ^ a) > ((t * t) & r))) {
    r = ((15u / (((2147483647u & y) & 7u) + 1u)) | ((2147483647u ^ z) | (b * 2147483647u)));
  } else {
    r = t;
  }
  if ((t != r)) {
    r = (a | (b & (x | r)));
  } else {
    r = y;
  }
  if (((x == 0u) && (y == 1u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
