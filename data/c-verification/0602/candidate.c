unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = (4294967295u >> (x & 31u));
  unsigned r = (((a << (b & 31u)) >> ((b >> (a & 31u)) & 31u)) / ((((~31u) & a) & 7u) + 1u));
  if ((((y << (y & 31u)) >> ((y / ((a & 7u) + 1u)) & 31u)) > 1u)) {
    r = (((r * b) ^ (2147483647u >> (a & 31u))) * a);
  } else {
    r = (r * x);
  }
  if (((x == 2147483647u) && (y == 4294967295u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
