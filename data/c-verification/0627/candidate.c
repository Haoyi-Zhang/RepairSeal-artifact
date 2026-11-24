unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned poison = (1u / (t ^ 1u));
  unsigned a = z;
  unsigned b = t;
  unsigned r = (a - a);
  if ((((2u ^ a) - 3u) == (t | (y + z)))) {
    r = 2u;
  } else {
    r = 2147483647u;
  }
  return r;
}
