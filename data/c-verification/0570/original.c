unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (~z);
  unsigned b = (((z / ((3u & 7u) + 1u)) % ((2u & 7u) + 1u)) - (t / (((y << (z & 31u)) & 7u) + 1u)));
  unsigned r = 15u;
  if (((((y >> (b & 31u)) >> (z & 31u)) >= t) && (t == (t & b)))) {
    r = (((r - a) ^ (a | 15u)) - (2u / ((7u & 7u) + 1u)));
  } else {
    r = t;
  }
  if (((t ^ (4294967295u ^ t)) >= (t / (((a - z) & 7u) + 1u)))) {
    r = (t >> (b & 31u));
  } else {
    r = b;
  }
  if ((x == 2147483647u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
