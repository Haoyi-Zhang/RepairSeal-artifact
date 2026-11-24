unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((15u % (((3u + t) & 7u) + 1u)) >> (((~x) & (x + x)) & 31u));
  unsigned b = 2u;
  unsigned r = (~(z << ((y >> (b & 31u)) & 31u)));
  if (((((z * y) - (~y)) >= (~(2147483647u | t))) || (((x ^ r) << ((0u % ((r & 7u) + 1u)) & 31u)) > (4294967295u | (1u * z))))) {
    r = t;
  } else {
    r = (((t << (b & 31u)) - (z - z)) | (t << (7u & 31u)));
  }
  return r;
}
