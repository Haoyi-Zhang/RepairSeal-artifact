unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((x * 4294967295u) - (x ^ x)) * x);
  unsigned b = (a * ((x % ((a & 7u) + 1u)) + (2u >> (x & 31u))));
  unsigned r = (z + a);
  if (((4294967295u | (1u % ((b & 7u) + 1u))) <= a)) {
    r = (r >> (2u & 31u));
  } else {
    r = a;
  }
  if ((((x ^ r) * (b | z)) == z)) {
    r = (r * 15u);
  } else {
    r = (r / ((((4294967295u >> (x & 31u)) & (~3u)) & 7u) + 1u));
  }
  return r;
}
