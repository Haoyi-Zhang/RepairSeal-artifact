unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = t;
  unsigned b = (t % ((x & 7u) + 1u));
  unsigned r = (t + (15u | (t / ((15u & 7u) + 1u))));
  if ((x == 31u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
