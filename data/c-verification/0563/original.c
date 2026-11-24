unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((~3u) + ((t | z) + 1u));
  unsigned b = (~y);
  unsigned r = 3u;
  if ((((a % ((b & 7u) + 1u)) ^ 3u) < a)) {
    r = b;
  } else {
    r = (31u * ((31u + 31u) * (~4294967295u)));
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
