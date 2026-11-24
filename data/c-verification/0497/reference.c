unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = ((2u / (((a - y) & 7u) + 1u)) & (a & (a << (x & 31u))));
  unsigned r = (((y & a) << (b & 31u)) / ((((x / ((a & 7u) + 1u)) % (((a + b) & 7u) + 1u)) & 7u) + 1u));
  if ((((~r) >> (r & 31u)) >= r)) {
    r = (1u % ((((b | x) / ((x & 7u) + 1u)) & 7u) + 1u));
  } else {
    r = (x | x);
  }
  if (((!((31u ^ (a * 31u)) == ((y | y) / ((3u & 7u) + 1u)))) && (4294967295u <= a))) {
    r = b;
  } else {
    r = a;
  }
  return r;
}
