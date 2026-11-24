unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (x >> (((~z) << (x & 31u)) & 31u));
  unsigned b = (a | ((z / ((x & 7u) + 1u)) | (7u | a)));
  unsigned r = (~((~4294967295u) | (x / ((b & 7u) + 1u))));
  if (((4294967295u - r) == ((31u + 0u) / ((r & 7u) + 1u)))) {
    r = (((y ^ b) << (x & 31u)) ^ (z << ((r / ((y & 7u) + 1u)) & 31u)));
  } else {
    r = a;
  }
  if (((x == 2147483648u) && (y == 32u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
