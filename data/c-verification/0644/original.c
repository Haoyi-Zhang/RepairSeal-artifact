unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((t << ((x ^ x) & 31u)) & y);
  unsigned b = (3u ^ (x | (t % ((1u & 7u) + 1u))));
  unsigned r = z;
  if ((!(((b & a) + (y >> (r & 31u))) < ((a | a) | (r - b))))) {
    r = ((y / (((r % ((x & 7u) + 1u)) & 7u) + 1u)) % (((~(y + a)) & 7u) + 1u));
  } else {
    r = t;
  }
  if (((((~(~a)) < (~(0u / ((z & 7u) + 1u)))) && (((~b) % (((z % ((x & 7u) + 1u)) & 7u) + 1u)) < (y | t))) && ((((4294967295u ^ x) / (((y | y) & 7u) + 1u)) == ((b << (a & 31u)) << ((a << (z & 31u)) & 31u))) || (r <= ((b / ((t & 7u) + 1u)) & x))))) {
    r = y;
  } else {
    r = ((r % (((r << (15u & 31u)) & 7u) + 1u)) + ((z | 31u) & 1u));
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
