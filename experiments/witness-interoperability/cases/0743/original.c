unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((y - x) << ((y ^ 31u) & 31u)) * (~x));
  unsigned b = a;
  unsigned r = b;
  if ((((~r) * (x / ((a & 7u) + 1u))) >= x)) {
    r = ((r ^ b) % (((y + 0u) & 7u) + 1u));
  } else {
    r = ((b << ((a + r) & 31u)) % ((r & 7u) + 1u));
  }
  if ((x == 32u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
