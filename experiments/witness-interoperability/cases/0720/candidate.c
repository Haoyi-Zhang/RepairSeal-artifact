unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (~t);
  unsigned b = (((z | x) % (((t / ((z & 7u) + 1u)) & 7u) + 1u)) << (((t * x) ^ 2147483647u) & 31u));
  unsigned r = (~(t & a));
  if ((t >= t)) {
    r = (((2147483647u - b) * (y & x)) + (z & (a | b)));
  } else {
    r = (((z / ((31u & 7u) + 1u)) >> (1u & 31u)) >> (((y >> (y & 31u)) & r) & 31u));
  }
  return r;
}
