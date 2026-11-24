unsigned f(unsigned x, unsigned y) {
  unsigned a = y;
  unsigned b = (((7u + y) / (((a % ((x & 7u) + 1u)) & 7u) + 1u)) * ((y + y) << (y & 31u)));
  unsigned r = (((x % ((a & 7u) + 1u)) & (a / ((2u & 7u) + 1u))) << (((b ^ b) * (0u * x)) & 31u));
  if (((x == 2147483648u) && (y == 31u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
