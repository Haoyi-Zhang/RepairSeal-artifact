unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = x;
  unsigned b = (~(z | z));
  unsigned r = (a << ((z | (a * b)) & 31u));
  if ((b == ((4294967295u >> (y & 31u)) * (a * b)))) {
    r = (((z & r) ^ (z >> (z & 31u))) % (((~(1u & x)) & 7u) + 1u));
  } else {
    r = (z | (y ^ 0u));
  }
  if ((((15u >> (z & 31u)) >> ((z << (x & 31u)) & 31u)) >= ((2u & 7u) ^ b))) {
    r = (x << ((r - (y << (7u & 31u))) & 31u));
  } else {
    r = ((~(1u % ((x & 7u) + 1u))) - (r >> ((b ^ x) & 31u)));
  }
  return r;
}
