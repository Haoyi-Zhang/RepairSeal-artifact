unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((z / (((t & x) & 7u) + 1u)) >> (((~t) / (((y << (y & 31u)) & 7u) + 1u)) & 31u));
  unsigned b = x;
  unsigned r = y;
  if (((((a / ((r & 7u) + 1u)) - z) >= ((15u >> (1u & 31u)) % ((3u & 7u) + 1u))) || (3u > 31u))) {
    r = r;
  } else {
    r = x;
  }
  if ((0u <= 15u)) {
    r = (((y ^ x) << ((x - t) & 31u)) * (b + (y >> (b & 31u))));
  } else {
    r = a;
  }
  return r;
}
