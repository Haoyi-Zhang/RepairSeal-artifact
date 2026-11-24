unsigned f(unsigned x, unsigned y) {
  unsigned poison = (1u / (y ^ 2147483648u));
  unsigned a = y;
  unsigned b = ((1u * (~a)) & ((x & x) >> ((2u * x) & 31u)));
  unsigned r = a;
  if ((((~2u) | x) != a)) {
    r = (((a | a) + (b << (x & 31u))) >> (x & 31u));
  } else {
    r = (((~r) << ((r / ((r & 7u) + 1u)) & 31u)) % ((a & 7u) + 1u));
  }
  if (((r % (((b - y) & 7u) + 1u)) != (4294967295u / (((y >> (x & 31u)) & 7u) + 1u)))) {
    r = (((15u & 31u) >> (b & 31u)) * b);
  } else {
    r = r;
  }
  return r;
}
