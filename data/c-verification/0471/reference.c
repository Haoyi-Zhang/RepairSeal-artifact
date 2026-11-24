unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = t;
  unsigned b = (((2147483647u ^ 1u) / ((z & 7u) + 1u)) * z);
  unsigned r = a;
  if ((b <= r)) {
    r = ((a ^ (y * x)) + (~1u));
  } else {
    r = (((z ^ 1u) - (r >> (x & 31u))) % ((((z / ((z & 7u) + 1u)) - (y ^ z)) & 7u) + 1u));
  }
  return r;
}
