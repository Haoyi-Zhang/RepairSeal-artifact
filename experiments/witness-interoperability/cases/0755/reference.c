unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (z | y);
  unsigned b = a;
  unsigned r = ((1u << ((15u % ((z & 7u) + 1u)) & 31u)) * 2147483647u);
  if ((x <= 7u)) {
    r = x;
  } else {
    r = (y / ((((z | z) / (((~x) & 7u) + 1u)) & 7u) + 1u));
  }
  if (((x % (((r % ((z & 7u) + 1u)) & 7u) + 1u)) == (x * (z / ((y & 7u) + 1u))))) {
    r = z;
  } else {
    r = (((3u % ((b & 7u) + 1u)) >> (z & 31u)) & 3u);
  }
  return r;
}
