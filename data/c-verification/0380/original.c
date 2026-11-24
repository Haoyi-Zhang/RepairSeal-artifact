unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = z;
  unsigned b = 31u;
  unsigned r = ((b + b) ^ (x << (y & 31u)));
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
