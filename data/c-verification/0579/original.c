unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = z;
  unsigned b = y;
  unsigned r = (2u + ((x | 15u) + x));
  if ((((x >> (x & 31u)) % (((y / ((4294967295u & 7u) + 1u)) & 7u) + 1u)) <= (~7u))) {
    r = (((b * r) & (y * a)) & (z + (2u + 31u)));
  } else {
    r = (((r | x) ^ (31u + 15u)) + y);
  }
  if ((z != 2147483647u)) {
    r = x;
  } else {
    r = (~((x % ((y & 7u) + 1u)) - (1u << (y & 31u))));
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
