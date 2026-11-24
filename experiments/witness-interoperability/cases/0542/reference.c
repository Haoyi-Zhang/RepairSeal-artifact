unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = 15u;
  unsigned b = ((a << ((t ^ y) & 31u)) & x);
  unsigned r = t;
  if (((r * t) < b)) {
    r = r;
  } else {
    r = 15u;
  }
  if (((a << ((t / ((b & 7u) + 1u)) & 31u)) > ((~z) % (((31u ^ z) & 7u) + 1u)))) {
    r = t;
  } else {
    r = (((x >> (t & 31u)) % (((y / ((b & 7u) + 1u)) & 7u) + 1u)) >> (b & 31u));
  }
  return r;
}
