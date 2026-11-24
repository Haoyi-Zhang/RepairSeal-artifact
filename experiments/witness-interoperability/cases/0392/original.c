unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (y | 7u);
  unsigned b = (((~z) - (z - z)) >> (a & 31u));
  unsigned r = t;
  if ((((15u | 15u) - a) <= (t ^ y))) {
    r = (~z);
  } else {
    r = t;
  }
  if ((!((((0u % ((y & 7u) + 1u)) & 4294967295u) >= 1u) || (((~z) + t) <= ((x << (a & 31u)) >> ((b * 2147483647u) & 31u)))))) {
    r = 31u;
  } else {
    r = r;
  }
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
