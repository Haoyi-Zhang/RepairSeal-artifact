unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (31u << ((7u + (t % ((t & 7u) + 1u))) & 31u));
  unsigned b = t;
  unsigned r = (((z + z) + (b / ((2u & 7u) + 1u))) / ((((t >> (x & 31u)) / (((3u * x) & 7u) + 1u)) & 7u) + 1u));
  if ((b < 3u)) {
    r = ((y >> (b & 31u)) * ((~b) / ((2147483647u & 7u) + 1u)));
  } else {
    r = 0u;
  }
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
