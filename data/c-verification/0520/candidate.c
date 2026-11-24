unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((z / ((y & 7u) + 1u)) ^ (7u + x)) ^ t);
  unsigned b = (((31u << (x & 31u)) ^ (0u | 7u)) / ((((y & 4294967295u) / (((4294967295u / ((y & 7u) + 1u)) & 7u) + 1u)) & 7u) + 1u));
  unsigned r = z;
  return r;
}
