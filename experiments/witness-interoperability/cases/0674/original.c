unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (1u + ((z * y) / (((2147483647u << (4294967295u & 31u)) & 7u) + 1u)));
  unsigned b = (~(2u * y));
  unsigned r = (((~1u) + (4294967295u & x)) % ((((b & a) - y) & 7u) + 1u));
  if (((r / ((b & 7u) + 1u)) < z)) {
    r = (b >> ((x << ((1u % ((4294967295u & 7u) + 1u)) & 31u)) & 31u));
  } else {
    r = x;
  }
  if (((((z | (~0u)) >= ((b >> (y & 31u)) % (((y % ((y & 7u) + 1u)) & 7u) + 1u))) || (x <= (~a))) && ((x <= ((b >> (b & 31u)) + (4294967295u - r))) || ((r & (b + b)) == y)))) {
    r = (0u | ((1u + 1u) ^ (a << (2u & 31u))));
  } else {
    r = (a ^ (r ^ (z - 31u)));
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
