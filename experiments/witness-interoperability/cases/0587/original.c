unsigned f(unsigned x, unsigned y) {
  unsigned a = (((x + x) & 2u) + ((y >> (y & 31u)) + (31u & x)));
  unsigned b = ((a | (y + y)) >> (a & 31u));
  unsigned r = (~(y * (1u + y)));
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
