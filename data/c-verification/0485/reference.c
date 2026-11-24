unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = t;
  unsigned b = (t - ((31u / ((15u & 7u) + 1u)) << ((1u + 2u) & 31u)));
  unsigned r = y;
  if (((1u / (((2u & z) & 7u) + 1u)) > (a - b))) {
    r = (((3u << (r & 31u)) * r) % ((b & 7u) + 1u));
  } else {
    r = 1u;
  }
  if (((z & (a & b)) < (15u >> (3u & 31u)))) {
    r = a;
  } else {
    r = (((a << (a & 31u)) + (~1u)) * ((x * a) * b));
  }
  return r;
}
