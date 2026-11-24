unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (y * (7u + y));
  unsigned b = (((15u | z) & (y >> (z & 31u))) % ((((y * 2147483647u) >> (z & 31u)) & 7u) + 1u));
  unsigned r = (z % ((((x ^ x) + (x % ((b & 7u) + 1u))) & 7u) + 1u));
  if (((!((~(y ^ a)) == ((~y) - (x % ((b & 7u) + 1u))))) || ((a * r) <= (r & x)))) {
    r = ((x % ((a & 7u) + 1u)) | 15u);
  } else {
    r = (((b & a) / (((z / ((x & 7u) + 1u)) & 7u) + 1u)) + ((b >> (r & 31u)) << ((2u * b) & 31u)));
  }
  return r;
}
