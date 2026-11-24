unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((~(y / ((x & 7u) + 1u))) & x);
  unsigned b = (((~z) ^ (z - x)) / ((((3u & t) >> ((a & 2147483647u) & 31u)) & 7u) + 1u));
  unsigned r = x;
  if ((((7u ^ t) << (a & 31u)) >= a)) {
    r = (b / ((((0u ^ 7u) - (r * b)) & 7u) + 1u));
  } else {
    r = ((2u ^ a) - ((7u % ((4294967295u & 7u) + 1u)) ^ 4294967295u));
  }
  if (((((3u * 31u) / (((a & 2147483647u) & 7u) + 1u)) < ((t >> (4294967295u & 31u)) ^ (y & y))) && ((a >= (~2147483647u)) || (x != b)))) {
    r = (b ^ ((b << (a & 31u)) / (((b + 31u) & 7u) + 1u)));
  } else {
    r = ((b % (((31u % ((3u & 7u) + 1u)) & 7u) + 1u)) & x);
  }
  return r;
}
