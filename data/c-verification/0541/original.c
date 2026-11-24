unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = 2u;
  unsigned b = (t * (t / ((31u & 7u) + 1u)));
  unsigned r = t;
  if ((!(2u >= x))) {
    r = (((r << (a & 31u)) ^ x) / ((((y & 4294967295u) >> ((r - y) & 31u)) & 7u) + 1u));
  } else {
    r = (b + (~(r | z)));
  }
  if ((x == 32u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
