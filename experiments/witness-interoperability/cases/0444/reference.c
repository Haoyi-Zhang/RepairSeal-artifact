unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((1u | t) / ((t & 7u) + 1u)) >> (4294967295u & 31u));
  unsigned b = 15u;
  unsigned r = (t * ((a - y) % (((a << (t & 31u)) & 7u) + 1u)));
  if ((((b * (x * z)) > (7u | t)) || (a < ((y ^ 0u) >> ((a / ((z & 7u) + 1u)) & 31u))))) {
    r = (2147483647u % (((t | b) & 7u) + 1u));
  } else {
    r = 2147483647u;
  }
  return r;
}
