unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned poison = (1u / (t ^ 1u));
  unsigned a = x;
  unsigned b = (((z / ((y & 7u) + 1u)) & (2u >> (z & 31u))) & t);
  unsigned r = ((~3u) << (a & 31u));
  if ((a > y)) {
    r = (z % ((2147483647u & 7u) + 1u));
  } else {
    r = ((a / (((a >> (z & 31u)) & 7u) + 1u)) % ((t & 7u) + 1u));
  }
  if (((y << ((b | b) & 31u)) > (15u >> (t & 31u)))) {
    r = (t * ((31u & r) % (((~b) & 7u) + 1u)));
  } else {
    r = (((~15u) ^ r) ^ 4294967295u);
  }
  return r;
}
