unsigned f(unsigned x, unsigned y) {
  unsigned a = ((~(y - x)) * (y << (y & 31u)));
  unsigned b = 1u;
  unsigned r = b;
  if ((((b >> (a & 31u)) | (15u * x)) >= r)) {
    r = (~4294967295u);
  } else {
    r = ((y + (r - x)) | ((b + 31u) & a));
  }
  if (((!(((x & 31u) << (x & 31u)) > (b - (b + a)))) && ((7u % ((r & 7u) + 1u)) == (1u - (~b))))) {
    r = (((b << (r & 31u)) << (3u & 31u)) / ((a & 7u) + 1u));
  } else {
    r = x;
  }
  return r;
}
