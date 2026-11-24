unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = z;
  unsigned b = (((z << (2147483647u & 31u)) >> (y & 31u)) & y);
  unsigned r = (~((y & 1u) ^ (b % ((x & 7u) + 1u))));
  if ((((0u & 31u) % ((a & 7u) + 1u)) <= ((z & z) % ((7u & 7u) + 1u)))) {
    r = 2u;
  } else {
    r = (a % ((((b + y) / ((31u & 7u) + 1u)) & 7u) + 1u));
  }
  if ((y != (~(r * x)))) {
    r = ((b << ((t / ((a & 7u) + 1u)) & 31u)) >> (((x * y) + (t - 4294967295u)) & 31u));
  } else {
    r = a;
  }
  return r;
}
