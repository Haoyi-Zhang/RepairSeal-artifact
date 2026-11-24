unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = 2u;
  unsigned b = (a << (((1u << (z & 31u)) << ((x << (0u & 31u)) & 31u)) & 31u));
  unsigned r = ((z + 3u) % ((y & 7u) + 1u));
  if (((~(z | r)) >= ((t + 3u) >> (t & 31u)))) {
    r = t;
  } else {
    r = (((a - r) + (a ^ b)) << (1u & 31u));
  }
  if ((((b << (t & 31u)) + (~3u)) < z)) {
    r = (((4294967295u * 15u) + a) >> (a & 31u));
  } else {
    r = ((x % (((x * 1u) & 7u) + 1u)) / ((2u & 7u) + 1u));
  }
  return r;
}
