unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (3u % ((2u & 7u) + 1u));
  unsigned b = (4294967295u << (((a & x) ^ (a % ((2147483647u & 7u) + 1u))) & 31u));
  unsigned r = b;
  if (((~(z & 3u)) <= ((15u & x) + z))) {
    r = (((b << (x & 31u)) >> ((15u >> (31u & 31u)) & 31u)) << (((x & r) - (y << (a & 31u))) & 31u));
  } else {
    r = (((a & 15u) + r) * ((y - a) << ((1u >> (x & 31u)) & 31u)));
  }
  if (((z | 7u) > r)) {
    r = (x + ((31u * y) * (r & x)));
  } else {
    r = r;
  }
  return r;
}
