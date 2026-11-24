unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (y << (y & 31u));
  unsigned b = (y ^ 0u);
  unsigned r = (((a - 2u) / (((3u % ((a & 7u) + 1u)) & 7u) + 1u)) * (2147483647u / ((2147483647u & 7u) + 1u)));
  if ((z == ((a | 7u) / ((a & 7u) + 1u)))) {
    r = (r + z);
  } else {
    r = (y % (((~(r + 3u)) & 7u) + 1u));
  }
  if (((~(z % ((r & 7u) + 1u))) <= ((y % ((7u & 7u) + 1u)) + (r << (r & 31u))))) {
    r = (0u << (z & 31u));
  } else {
    r = (r & a);
  }
  if (((x == 4294967295u) && (y == 3u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
