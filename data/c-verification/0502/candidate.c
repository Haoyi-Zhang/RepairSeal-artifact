unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (~(y / (((y + 2u) & 7u) + 1u)));
  unsigned b = (((y + z) & (t ^ x)) ^ ((15u - 1u) & t));
  unsigned r = x;
  if (((y << (r & 31u)) == ((z - 7u) << ((x & b) & 31u)))) {
    r = (t | ((t + 2u) ^ (r % ((2u & 7u) + 1u))));
  } else {
    r = (((r - r) | y) * (15u % (((a / ((2147483647u & 7u) + 1u)) & 7u) + 1u)));
  }
  if (((x == 31u) && (y == 32u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
