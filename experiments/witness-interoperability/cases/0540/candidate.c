unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((2147483647u | x) + (~x)) ^ ((z + x) | (z << (0u & 31u))));
  unsigned b = ((a & a) & y);
  unsigned r = z;
  if ((((z >> (r & 31u)) >> ((31u ^ z) & 31u)) != ((b | x) + (b << (z & 31u))))) {
    r = ((b + (1u ^ z)) - ((y * 2147483647u) / ((1u & 7u) + 1u)));
  } else {
    r = b;
  }
  if (((((a | y) | (z & r)) >= ((x - z) % ((x & 7u) + 1u))) || ((15u <= (b + (3u & x))) && (a > 1u)))) {
    r = (((z & b) - y) + ((r / ((y & 7u) + 1u)) / ((b & 7u) + 1u)));
  } else {
    r = (2147483647u | a);
  }
  return r;
}
