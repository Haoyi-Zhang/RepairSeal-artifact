unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((y - 0u) / (((y << ((x ^ x) & 31u)) & 7u) + 1u));
  unsigned b = (15u * ((z / ((z & 7u) + 1u)) - (z / ((t & 7u) + 1u))));
  unsigned r = y;
  if ((((r * t) >> ((1u | x) & 31u)) <= (a | b))) {
    r = ((z * (1u & t)) % ((z & 7u) + 1u));
  } else {
    r = 7u;
  }
  if ((((15u & z) & (a | y)) <= ((y >> (15u & 31u)) * 1u))) {
    r = (x ^ a);
  } else {
    r = (r + ((r - a) - y));
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
