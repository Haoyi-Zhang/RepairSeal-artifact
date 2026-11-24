unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (~((x * 0u) ^ (x % ((y & 7u) + 1u))));
  unsigned b = y;
  unsigned r = (~a);
  if (((!((~(y >> (b & 31u))) >= y)) || (a != b))) {
    r = (~((t / ((z & 7u) + 1u)) << ((0u << (2u & 31u)) & 31u)));
  } else {
    r = y;
  }
  if ((y <= ((15u | 15u) & (2147483647u | 7u)))) {
    r = (~b);
  } else {
    r = (b ^ ((x - 0u) >> (7u & 31u)));
  }
  if (((x == 31u) && (y == 0u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
