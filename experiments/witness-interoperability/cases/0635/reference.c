unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = x;
  unsigned b = (2u | z);
  unsigned r = (~(y ^ (x | 3u)));
  if ((z > ((3u | x) % (((x ^ r) & 7u) + 1u)))) {
    r = ((r - 4294967295u) - r);
  } else {
    r = a;
  }
  return r;
}
