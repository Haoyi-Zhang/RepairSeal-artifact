unsigned f(unsigned x, unsigned y) {
  unsigned a = ((~(y & x)) % ((x & 7u) + 1u));
  unsigned b = a;
  unsigned r = (((x >> (x & 31u)) - (x % ((y & 7u) + 1u))) * x);
  if (((b <= (r | (r ^ x))) && ((~(r | a)) > ((x & x) | (a & y))))) {
    r = (((4294967295u & r) ^ (~r)) << ((x ^ 0u) & 31u));
  } else {
    r = (((x ^ b) * a) | ((a ^ a) / ((x & 7u) + 1u)));
  }
  if ((((x & x) ^ (r >> (15u & 31u))) <= (~x))) {
    r = ((~r) + x);
  } else {
    r = 3u;
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
