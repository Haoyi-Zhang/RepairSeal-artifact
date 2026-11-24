unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((z >> (z & 31u)) << ((2u ^ z) & 31u)) / (((7u - y) & 7u) + 1u));
  unsigned b = (~((x % ((2u & 7u) + 1u)) >> ((7u - z) & 31u)));
  unsigned r = y;
  if ((((z / ((b & 7u) + 1u)) - (r | b)) > ((z ^ a) ^ (y << (x & 31u))))) {
    r = (((7u + y) >> ((2147483647u | x) & 31u)) + z);
  } else {
    r = (~((z / ((z & 7u) + 1u)) * (2147483647u << (15u & 31u))));
  }
  if ((((z ^ (r << (r & 31u))) >= ((y % ((b & 7u) + 1u)) - (b / ((b & 7u) + 1u)))) || (((b * r) % (((z << (b & 31u)) & 7u) + 1u)) > x))) {
    r = r;
  } else {
    r = (z - ((~r) + y));
  }
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
