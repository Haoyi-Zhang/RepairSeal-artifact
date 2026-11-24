unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((~z) >> (x & 31u)) << ((3u ^ 3u) & 31u));
  unsigned b = ((3u & (~t)) - ((y + z) * (a - t)));
  unsigned r = (x + 7u);
  if (((x == 4294967295u) && (y == 3u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
