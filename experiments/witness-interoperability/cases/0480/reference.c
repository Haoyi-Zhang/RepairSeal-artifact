unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((0u << ((t * x) & 31u)) << (((t ^ 7u) % (((y & y) & 7u) + 1u)) & 31u));
  unsigned b = a;
  unsigned r = (((31u * a) + y) % ((y & 7u) + 1u));
  if (((a | (y ^ t)) != ((x ^ t) / (((t + 4294967295u) & 7u) + 1u)))) {
    r = r;
  } else {
    r = (x % (((t & (7u / ((b & 7u) + 1u))) & 7u) + 1u));
  }
  if ((!(((b << (15u & 31u)) & (2u | t)) != (a / (((t - 3u) & 7u) + 1u))))) {
    r = (z / (((a << (x & 31u)) & 7u) + 1u));
  } else {
    r = (((x / ((x & 7u) + 1u)) & (x + b)) * b);
  }
  return r;
}
