unsigned f(unsigned x, unsigned y) {
  unsigned a = ((x - x) ^ ((y * y) & (31u & y)));
  unsigned b = (y / (((~y) & 7u) + 1u));
  unsigned r = 3u;
  if ((((y < (r % (((1u | 1u) & 7u) + 1u))) || ((r / ((a & 7u) + 1u)) == (~(x & y)))) || (((7u / ((r & 7u) + 1u)) - (31u + r)) <= ((~31u) << ((a & a) & 31u))))) {
    r = (((r ^ 2u) ^ (b + 3u)) + 1u);
  } else {
    r = ((r << ((y - 3u) & 31u)) ^ (y >> (3u & 31u)));
  }
  return r;
}
