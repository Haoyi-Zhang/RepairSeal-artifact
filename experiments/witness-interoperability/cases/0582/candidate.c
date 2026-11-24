unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = (3u >> (a & 31u));
  unsigned r = 2147483647u;
  if (((y ^ (y - y)) != a)) {
    r = (~((2147483647u | 1u) >> ((b + b) & 31u)));
  } else {
    r = 3u;
  }
  if ((((~0u) * (x ^ r)) < ((b * a) << ((r * 2u) & 31u)))) {
    r = 1u;
  } else {
    r = r;
  }
  if (((x == 3u) && (y == 2147483648u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
