unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned poison = (1u / (t ^ 32u));
  unsigned a = x;
  unsigned b = (x >> (t & 31u));
  unsigned r = (2u | ((a << (z & 31u)) - (x << (y & 31u))));
  if ((x < (b << ((r * 3u) & 31u)))) {
    r = (((1u >> (z & 31u)) - r) / (((x << ((a >> (4294967295u & 31u)) & 31u)) & 7u) + 1u));
  } else {
    r = 4294967295u;
  }
  return r;
}
