unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = 2u;
  unsigned b = a;
  unsigned r = (((z - 3u) / (((x / ((2u & 7u) + 1u)) & 7u) + 1u)) % ((z & 7u) + 1u));
  if ((((2147483647u | z) ^ a) > ((r >> (x & 31u)) / (((z >> (y & 31u)) & 7u) + 1u)))) {
    r = (((x & b) % (((a % ((r & 7u) + 1u)) & 7u) + 1u)) + ((z - z) % (((z >> (15u & 31u)) & 7u) + 1u)));
  } else {
    r = (((x << (b & 31u)) / (((b & 2u) & 7u) + 1u)) << ((a << (a & 31u)) & 31u));
  }
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
