unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = (((y + 15u) * 15u) - (y + (a * y)));
  unsigned r = ((b ^ (a << (15u & 31u))) + b);
  if ((!(((2147483647u % (((y % ((y & 7u) + 1u)) & 7u) + 1u)) > (0u & a)) && ((r & (x | a)) >= ((r | r) / ((b & 7u) + 1u)))))) {
    r = (((y / ((r & 7u) + 1u)) << (a & 31u)) | ((r * b) - (15u * 31u)));
  } else {
    r = (~b);
  }
  if (((b << (a & 31u)) <= x)) {
    r = (((~r) >> ((x << (y & 31u)) & 31u)) - ((r ^ a) >> (b & 31u)));
  } else {
    r = (((~3u) >> ((1u * b) & 31u)) | ((a * 1u) << (a & 31u)));
  }
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
