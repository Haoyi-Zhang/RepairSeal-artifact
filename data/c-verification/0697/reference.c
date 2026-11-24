unsigned f(unsigned x, unsigned y) {
  unsigned a = (y / ((((y * 7u) ^ (x / ((4294967295u & 7u) + 1u))) & 7u) + 1u));
  unsigned b = ((15u - (~y)) | x);
  unsigned r = (~((a % ((a & 7u) + 1u)) / (((b / ((1u & 7u) + 1u)) & 7u) + 1u)));
  if ((((x & a) - (a / ((x & 7u) + 1u))) > b)) {
    r = (((a << (x & 31u)) >> ((y ^ 1u) & 31u)) & ((r | 2u) >> (x & 31u)));
  } else {
    r = (y ^ a);
  }
  if ((((4294967295u % (((r & x) & 7u) + 1u)) != (~(r % ((x & 7u) + 1u)))) || (!(r > (b + (7u * b)))))) {
    r = (((~r) * 1u) | (r * (y % ((4294967295u & 7u) + 1u))));
  } else {
    r = (r * 7u);
  }
  return r;
}
