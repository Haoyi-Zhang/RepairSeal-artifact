unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (x | ((x | y) - (x * x)));
  unsigned b = (z << (4294967295u & 31u));
  unsigned r = (~((31u & a) | z));
  if (((x == 2147483647u) && (y == 2147483648u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
