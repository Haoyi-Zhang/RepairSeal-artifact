unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = 7u;
  unsigned b = (~((15u >> (a & 31u)) & 15u));
  unsigned r = (a & ((y % ((4294967295u & 7u) + 1u)) - b));
  if ((!((a & x) != y))) {
    r = x;
  } else {
    r = (((y >> (z & 31u)) + b) | ((b >> (b & 31u)) * (a - 15u)));
  }
  if ((((t != ((31u * 2u) / (((z & t) & 7u) + 1u))) || (b >= (~2u))) || (y < z))) {
    r = r;
  } else {
    r = z;
  }
  if ((x == 2147483647u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
