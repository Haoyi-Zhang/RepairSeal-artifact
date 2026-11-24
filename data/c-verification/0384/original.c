unsigned f(unsigned x, unsigned y) {
  unsigned a = (1u << (4294967295u & 31u));
  unsigned b = (((a | x) ^ (a + 0u)) ^ (0u / ((a & 7u) + 1u)));
  unsigned r = x;
  if ((((0u | b) ^ (~r)) > (r + (31u | b)))) {
    r = (2u & 1u);
  } else {
    r = (x + ((r << (4294967295u & 31u)) >> ((r >> (b & 31u)) & 31u)));
  }
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
