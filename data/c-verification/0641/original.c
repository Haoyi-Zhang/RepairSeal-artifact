unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((t & (z & t)) >> (x & 31u));
  unsigned b = ((~(t >> (3u & 31u))) & (t + (a ^ t)));
  unsigned r = (((y - 3u) << (t & 31u)) - (b | (a * 2147483647u)));
  if (((((a * b) << ((31u ^ b) & 31u)) > z) || ((0u * (y + b)) != y))) {
    r = (~t);
  } else {
    r = 31u;
  }
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
