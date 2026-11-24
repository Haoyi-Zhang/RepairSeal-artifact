unsigned f(unsigned x, unsigned y) {
  unsigned a = (~(4294967295u * 0u));
  unsigned b = 15u;
  unsigned r = (b * ((b ^ a) << ((a / ((2u & 7u) + 1u)) & 31u)));
  if ((!(!(((7u | x) + 2u) < ((2147483647u + 1u) << ((a % ((x & 7u) + 1u)) & 31u)))))) {
    r = y;
  } else {
    r = (4294967295u + ((y << (y & 31u)) + 31u));
  }
  if ((((15u / ((a & 7u) + 1u)) & (7u ^ a)) > ((b >> (y & 31u)) * (a + 7u)))) {
    r = (~4294967295u);
  } else {
    r = y;
  }
  if (((x == 31u) && (y == 2147483648u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
