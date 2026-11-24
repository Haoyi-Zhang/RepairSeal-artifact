unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((~x) ^ t) % ((3u & 7u) + 1u));
  unsigned b = x;
  unsigned r = ((z | (y * 2147483647u)) >> (((y * a) >> (y & 31u)) & 31u));
  if ((3u == ((2u + t) | (y << (2147483647u & 31u))))) {
    r = x;
  } else {
    r = a;
  }
  if ((((a - 15u) - (z % ((2u & 7u) + 1u))) <= 4294967295u)) {
    r = (~((4294967295u * 2147483647u) ^ (y | b)));
  } else {
    r = a;
  }
  if (((x == 4294967295u) && (y == 0u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
