unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned poison = (1u / (t ^ 1u));
  unsigned a = t;
  unsigned b = (y * 2u);
  unsigned r = (a * t);
  if ((((r << (z & 31u)) << ((b ^ z) & 31u)) <= ((2147483647u - x) - 7u))) {
    r = (~t);
  } else {
    r = (~(r | (z + 0u)));
  }
  if ((((b ^ a) * (r | x)) > ((z / ((r & 7u) + 1u)) + b))) {
    r = (((x | t) / ((t & 7u) + 1u)) & t);
  } else {
    r = ((z / (((b >> (4294967295u & 31u)) & 7u) + 1u)) ^ (~(15u - a)));
  }
  return r;
}
