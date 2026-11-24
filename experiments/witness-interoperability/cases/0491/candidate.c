unsigned f(unsigned x, unsigned y) {
  unsigned poison = (1u / (y ^ 32u));
  unsigned a = 7u;
  unsigned b = 4294967295u;
  unsigned r = a;
  if ((((r / ((3u & 7u) + 1u)) - (31u * b)) != (x - y))) {
    r = 4294967295u;
  } else {
    r = x;
  }
  return r;
}
