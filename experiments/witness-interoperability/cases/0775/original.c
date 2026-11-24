unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = x;
  unsigned b = x;
  unsigned r = (((2u << (31u & 31u)) - a) % ((((~1u) >> ((y - y) & 31u)) & 7u) + 1u));
  if ((!((z + (r * x)) < 15u))) {
    r = (((b << (r & 31u)) / ((x & 7u) + 1u)) + (b ^ (31u % ((z & 7u) + 1u))));
  } else {
    r = (x | r);
  }
  if (((((b | 1u) > (b / (((z / ((a & 7u) + 1u)) & 7u) + 1u))) || (x < ((r ^ y) | 3u))) || (((y ^ r) / (((r & r) & 7u) + 1u)) == z))) {
    r = (y & ((~3u) >> ((z / ((r & 7u) + 1u)) & 31u)));
  } else {
    r = (((2147483647u | 0u) << (r & 31u)) ^ (~(a % ((y & 7u) + 1u))));
  }
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
