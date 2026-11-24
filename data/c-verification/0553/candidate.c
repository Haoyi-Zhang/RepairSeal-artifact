unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((x << (y & 31u)) | x) + (y >> ((z + x) & 31u)));
  unsigned b = (((~0u) + (x + 2u)) * ((z - a) % (((1u * 2147483647u) & 7u) + 1u)));
  unsigned r = (((x << (z & 31u)) | z) & (~(y - y)));
  if (((((~b) | (b << (x & 31u))) < r) || (7u > 2147483647u))) {
    r = b;
  } else {
    r = (a * ((x - 2u) & r));
  }
  if ((1u > ((r / ((4294967295u & 7u) + 1u)) | (y % ((y & 7u) + 1u))))) {
    r = x;
  } else {
    r = ((x & (z & a)) - (~(y % ((y & 7u) + 1u))));
  }
  if (((x == 2147483647u) && (y == 1u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
