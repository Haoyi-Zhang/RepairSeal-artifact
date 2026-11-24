unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = x;
  unsigned b = (z - 2u);
  unsigned r = 4294967295u;
  if (((3u & (~r)) >= ((x & x) + (2147483647u - r)))) {
    r = y;
  } else {
    r = a;
  }
  if ((((x % ((4294967295u & 7u) + 1u)) % (((t + z) & 7u) + 1u)) <= (2u & (z >> (z & 31u))))) {
    r = b;
  } else {
    r = 31u;
  }
  return r;
}
