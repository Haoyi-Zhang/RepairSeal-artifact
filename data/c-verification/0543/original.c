unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((y * (y - y)) - ((~z) * (~y)));
  unsigned b = ((~(1u * y)) * ((x >> (a & 31u)) | 31u));
  unsigned r = x;
  if ((((4294967295u + b) / ((4294967295u & 7u) + 1u)) == 2147483647u)) {
    r = 2u;
  } else {
    r = (((4294967295u % ((a & 7u) + 1u)) * (x * r)) * (a % (((b << (a & 31u)) & 7u) + 1u)));
  }
  if (((y == ((b - 7u) ^ (r | a))) && ((((2u * r) >> (z & 31u)) < (z / (((3u * a) & 7u) + 1u))) && (((15u % ((r & 7u) + 1u)) >> ((1u / ((y & 7u) + 1u)) & 31u)) > x)))) {
    r = x;
  } else {
    r = (((31u * 2u) % (((a + b) & 7u) + 1u)) & x);
  }
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
