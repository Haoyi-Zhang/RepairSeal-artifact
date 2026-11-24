unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = x;
  unsigned b = (((z - z) >> ((7u | y) & 31u)) >> (((t | z) / ((t & 7u) + 1u)) & 31u));
  unsigned r = y;
  if ((!((z & (z * 3u)) <= (z >> ((~b) & 31u))))) {
    r = (t / ((((y * z) % (((0u * t) & 7u) + 1u)) & 7u) + 1u));
  } else {
    r = (((31u >> (a & 31u)) % ((b & 7u) + 1u)) % ((((t * t) >> (b & 31u)) & 7u) + 1u));
  }
  if (((x == 2147483648u) && (y == 3u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
