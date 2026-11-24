unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((0u | z) << ((x + y) & 31u)) - 1u);
  unsigned b = (a >> (x & 31u));
  unsigned r = z;
  if ((((~b) | a) <= 2147483647u)) {
    r = a;
  } else {
    r = (((7u ^ 15u) << ((4294967295u >> (a & 31u)) & 31u)) % ((2147483647u & 7u) + 1u));
  }
  if (((((b | t) * (b + x)) <= ((b << (r & 31u)) >> ((z << (t & 31u)) & 31u))) || (1u < ((x - r) * (x << (z & 31u)))))) {
    r = r;
  } else {
    r = (y ^ ((~t) ^ (a >> (y & 31u))));
  }
  return r;
}
