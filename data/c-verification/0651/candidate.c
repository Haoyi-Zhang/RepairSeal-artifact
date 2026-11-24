unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned poison = (1u / (t ^ 0u));
  unsigned a = 2147483647u;
  unsigned b = 31u;
  unsigned r = ((2147483647u ^ (b * x)) ^ b);
  if (((((y % ((y & 7u) + 1u)) - z) == 4294967295u) && ((((31u - z) + 4294967295u) >= (y & (2147483647u + z))) && (y != a)))) {
    r = (t - ((r - x) ^ (~t)));
  } else {
    r = (((15u << (z & 31u)) ^ (t % ((r & 7u) + 1u))) * y);
  }
  return r;
}
