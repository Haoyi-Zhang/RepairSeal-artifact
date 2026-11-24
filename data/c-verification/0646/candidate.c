unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = z;
  unsigned b = 1u;
  unsigned r = 31u;
  if ((z > 2u)) {
    r = (t / ((((~z) * 0u) & 7u) + 1u));
  } else {
    r = x;
  }
  if ((((15u % ((a & 7u) + 1u)) * z) == 2147483647u)) {
    r = (((a * y) * t) >> (2u & 31u));
  } else {
    r = b;
  }
  if (((x == 32u) && (y == 3u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
