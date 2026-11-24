unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (31u * (y % ((x & 7u) + 1u)));
  unsigned b = (((y ^ y) ^ z) % ((y & 7u) + 1u));
  unsigned r = (y << ((3u << ((x - 2u) & 31u)) & 31u));
  if ((((b * a) ^ (z >> (x & 31u))) <= ((z ^ r) / ((a & 7u) + 1u)))) {
    r = y;
  } else {
    r = a;
  }
  if ((x == 3u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
