unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = t;
  unsigned b = (~(31u % ((15u & 7u) + 1u)));
  unsigned r = (y + ((z >> (31u & 31u)) + (3u * z)));
  if (((((z >> (a & 31u)) / (((t * x) & 7u) + 1u)) != t) || (!(1u > t)))) {
    r = (((~3u) & (x % ((2147483647u & 7u) + 1u))) >> (a & 31u));
  } else {
    r = x;
  }
  return r;
}
