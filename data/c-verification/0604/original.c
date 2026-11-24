unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (4294967295u / ((y & 7u) + 1u));
  unsigned b = y;
  unsigned r = a;
  if ((!(((x >> ((1u ^ t) & 31u)) > y) && ((2147483647u ^ t) == t)))) {
    r = z;
  } else {
    r = (~z);
  }
  if ((x == 2u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
