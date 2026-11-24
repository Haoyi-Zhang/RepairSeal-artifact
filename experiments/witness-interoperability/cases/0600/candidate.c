unsigned f(unsigned x, unsigned y) {
  unsigned a = (((y >> (y & 31u)) - (31u * 7u)) - (x | (3u + x)));
  unsigned b = (((a % ((x & 7u) + 1u)) ^ y) + ((y % ((2u & 7u) + 1u)) % ((15u & 7u) + 1u)));
  unsigned r = (((~x) + (7u % ((y & 7u) + 1u))) & (b & x));
  if ((a >= (~(b | r)))) {
    r = 31u;
  } else {
    r = (((b ^ 2u) + (~r)) / (((a >> ((15u * a) & 31u)) & 7u) + 1u));
  }
  if ((r >= ((b / ((y & 7u) + 1u)) % (((r & b) & 7u) + 1u)))) {
    r = 0u;
  } else {
    r = x;
  }
  return r;
}
