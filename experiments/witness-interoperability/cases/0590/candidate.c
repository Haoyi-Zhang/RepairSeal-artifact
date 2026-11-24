unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((z + z) / (((y | x) & 7u) + 1u)) * (0u << (y & 31u)));
  unsigned b = y;
  unsigned r = ((a ^ (z % ((b & 7u) + 1u))) + ((z ^ b) ^ (y + x)));
  if (((x == 0u) && (y == 3u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
