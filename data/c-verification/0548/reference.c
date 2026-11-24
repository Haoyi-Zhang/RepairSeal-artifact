unsigned f(unsigned x, unsigned y) {
  unsigned a = (((y % ((x & 7u) + 1u)) / (((x ^ y) & 7u) + 1u)) + y);
  unsigned b = ((x | (x >> (y & 31u))) * ((a << (y & 31u)) - (a ^ a)));
  unsigned r = 7u;
  if ((!((x != r) || (y != ((x / ((b & 7u) + 1u)) ^ (b / ((7u & 7u) + 1u))))))) {
    r = 1u;
  } else {
    r = x;
  }
  return r;
}
