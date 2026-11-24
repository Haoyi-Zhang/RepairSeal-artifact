unsigned f(unsigned x, unsigned y) {
  unsigned a = x;
  unsigned b = 31u;
  unsigned r = (3u + ((a | b) - (y / ((b & 7u) + 1u))));
  if (((x == 0u) && (y == 2u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
