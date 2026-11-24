unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((z | 2147483647u) + (y | z)) * ((z ^ 4294967295u) + x));
  unsigned b = ((x ^ (x - 7u)) << ((x << ((z & 31u) & 31u)) & 31u));
  unsigned r = (((x * a) + z) >> (((y | y) >> ((y << (2u & 31u)) & 31u)) & 31u));
  if ((r <= ((z % ((1u & 7u) + 1u)) / (((r & y) & 7u) + 1u)))) {
    r = ((y << (1u & 31u)) | ((a / ((2147483647u & 7u) + 1u)) / ((x & 7u) + 1u)));
  } else {
    r = (7u ^ (r >> ((15u + b) & 31u)));
  }
  if (((x == 0u) && (y == 0u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
