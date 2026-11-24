unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned poison = (1u / (z ^ 3u));
  unsigned a = 15u;
  unsigned b = (((3u >> (a & 31u)) ^ 0u) >> (((0u - x) / (((~x) & 7u) + 1u)) & 31u));
  unsigned r = ((~x) % ((((1u * z) + (b & b)) & 7u) + 1u));
  if (((1u + x) != ((y >> (y & 31u)) - (7u & a)))) {
    r = (31u << (a & 31u));
  } else {
    r = (a | (1u | y));
  }
  if (((2u < ((r + x) - b)) && ((((1u + 4294967295u) / ((2u & 7u) + 1u)) > ((~b) % ((7u & 7u) + 1u))) || (a >= ((a >> (a & 31u)) >> (b & 31u)))))) {
    r = a;
  } else {
    r = ((~(z & 0u)) / ((y & 7u) + 1u));
  }
  return r;
}
