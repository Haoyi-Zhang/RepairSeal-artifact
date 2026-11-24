unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = 2u;
  unsigned b = (~((15u | 2147483647u) - (a & z)));
  unsigned r = t;
  if (((z << (a & 31u)) > a)) {
    r = z;
  } else {
    r = (x & (1u * r));
  }
  if ((x <= b)) {
    r = (((z ^ a) | (t << (x & 31u))) + ((4294967295u >> (3u & 31u)) ^ (z * 31u)));
  } else {
    r = 1u;
  }
  return r;
}
