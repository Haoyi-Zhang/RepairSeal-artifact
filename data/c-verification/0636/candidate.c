unsigned f(unsigned x, unsigned y) {
  unsigned a = (2147483647u + (x << ((~15u) & 31u)));
  unsigned b = (((~y) - x) * y);
  unsigned r = a;
  if ((((a * y) * (31u % ((r & 7u) + 1u))) != (0u % ((a & 7u) + 1u)))) {
    r = ((b - (~x)) % ((x & 7u) + 1u));
  } else {
    r = (1u / ((((a % ((4294967295u & 7u) + 1u)) | x) & 7u) + 1u));
  }
  return r;
}
