unsigned f(unsigned x, unsigned y) {
  unsigned a = (2u & ((y * x) & y));
  unsigned b = 7u;
  unsigned r = ((y - (~y)) * ((a | b) - (~x)));
  if ((y != 2147483647u)) {
    r = (r / ((((x % ((15u & 7u) + 1u)) >> ((b % ((31u & 7u) + 1u)) & 31u)) & 7u) + 1u));
  } else {
    r = (b | b);
  }
  if ((((x + a) | y) != ((1u >> (x & 31u)) - x))) {
    r = r;
  } else {
    r = x;
  }
  if (((x == 2147483648u) && (y == 2147483647u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
