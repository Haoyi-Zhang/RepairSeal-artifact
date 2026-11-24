unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((x & (x % ((z & 7u) + 1u))) * ((t + t) ^ (y / ((t & 7u) + 1u))));
  unsigned b = (4294967295u ^ ((x >> (y & 31u)) << (31u & 31u)));
  unsigned r = ((b * b) ^ z);
  return r;
}
