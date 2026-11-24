unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((z + x) | x) >> (31u & 31u));
  unsigned b = (((z / ((4294967295u & 7u) + 1u)) / ((a & 7u) + 1u)) >> (((31u >> (15u & 31u)) - (x * y)) & 31u));
  unsigned r = x;
  if (((((z | (b >> (15u & 31u))) == ((0u / ((15u & 7u) + 1u)) & (x + 0u))) || (3u < z)) || ((x != x) || ((~(z - z)) > r)))) {
    r = (~(a << (3u & 31u)));
  } else {
    r = ((~x) << (z & 31u));
  }
  if ((((b | (b / ((a & 7u) + 1u))) == ((b * a) - (b + r))) || (y > (~(b / ((b & 7u) + 1u)))))) {
    r = a;
  } else {
    r = 2u;
  }
  return r;
}
