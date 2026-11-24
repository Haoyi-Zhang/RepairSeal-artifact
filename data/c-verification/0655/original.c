unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = x;
  unsigned b = a;
  unsigned r = ((b / ((2147483647u & 7u) + 1u)) + (x / (((b + y) & 7u) + 1u)));
  if ((((x >> (b & 31u)) * (r & y)) > 31u)) {
    r = (2147483647u / ((((~z) + (a - a)) & 7u) + 1u));
  } else {
    r = (3u | (x % (((r ^ 4294967295u) & 7u) + 1u)));
  }
  if (((3u & (a & x)) < (4294967295u + (~r)))) {
    r = (x - ((31u % ((x & 7u) + 1u)) * (r / ((x & 7u) + 1u))));
  } else {
    r = (((3u >> (2147483647u & 31u)) & (2147483647u / ((x & 7u) + 1u))) / ((1u & 7u) + 1u));
  }
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
