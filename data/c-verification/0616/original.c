unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((x * t) >> (((~y) % ((z & 7u) + 1u)) & 31u));
  unsigned b = (((a + z) << ((a ^ x) & 31u)) - a);
  unsigned r = ((y / (((t % ((b & 7u) + 1u)) & 7u) + 1u)) - ((b % ((2147483647u & 7u) + 1u)) << (y & 31u)));
  if ((z >= (b - (a - 0u)))) {
    r = (y / ((((z ^ 15u) * r) & 7u) + 1u));
  } else {
    r = x;
  }
  if ((15u > ((0u | a) ^ (x + x)))) {
    r = (4294967295u << (x & 31u));
  } else {
    r = ((2147483647u % (((~a) & 7u) + 1u)) >> (r & 31u));
  }
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
