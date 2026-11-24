unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (15u >> ((x % (((3u >> (x & 31u)) & 7u) + 1u)) & 31u));
  unsigned b = (((4294967295u / ((y & 7u) + 1u)) % (((z ^ 31u) & 7u) + 1u)) & t);
  unsigned r = a;
  if (((~a) <= t)) {
    r = (r << (z & 31u));
  } else {
    r = (((7u - 3u) / ((y & 7u) + 1u)) + ((4294967295u * 31u) * (t / ((x & 7u) + 1u))));
  }
  if ((((a % ((7u & 7u) + 1u)) >> ((t >> (z & 31u)) & 31u)) >= ((a * a) >> ((2u % ((31u & 7u) + 1u)) & 31u)))) {
    r = (~((t % ((r & 7u) + 1u)) >> (a & 31u)));
  } else {
    r = ((b >> (x & 31u)) + ((a + 2u) | (a + 4294967295u)));
  }
  return r;
}
