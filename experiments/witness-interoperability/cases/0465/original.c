unsigned f(unsigned x, unsigned y) {
  unsigned a = (~x);
  unsigned b = y;
  unsigned r = ((x & b) | a);
  if ((((b >> (x & 31u)) / (((y / ((a & 7u) + 1u)) & 7u) + 1u)) != a)) {
    r = a;
  } else {
    r = x;
  }
  if ((((((0u | x) | 0u) < 2147483647u) && (((~x) >> ((x | a) & 31u)) == ((y / ((x & 7u) + 1u)) >> ((2147483647u - b) & 31u)))) || (((a | r) | a) < a))) {
    r = y;
  } else {
    r = (((x ^ a) << ((b >> (2u & 31u)) & 31u)) >> ((r << ((x % ((x & 7u) + 1u)) & 31u)) & 31u));
  }
  if ((x == 31u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
