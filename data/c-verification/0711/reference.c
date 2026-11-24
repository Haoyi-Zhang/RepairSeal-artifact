unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = z;
  unsigned b = ((a | (2u << (x & 31u))) % (((y + y) & 7u) + 1u));
  unsigned r = (((a - 15u) + (2147483647u | b)) / ((4294967295u & 7u) + 1u));
  if (((y + 0u) != ((z | y) / ((a & 7u) + 1u)))) {
    r = (((z % ((y & 7u) + 1u)) * z) & (~(a / ((b & 7u) + 1u))));
  } else {
    r = b;
  }
  if ((((7u + 0u) - (~b)) <= (~y))) {
    r = x;
  } else {
    r = (((4294967295u << (z & 31u)) - (y ^ x)) / (((~(b << (y & 31u))) & 7u) + 1u));
  }
  return r;
}
