unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (((z / ((z & 7u) + 1u)) << (z & 31u)) | ((z | 31u) >> ((x - x) & 31u)));
  unsigned b = 31u;
  unsigned r = b;
  if ((((z ^ 4294967295u) << ((15u | a) & 31u)) > ((4294967295u >> (x & 31u)) * (31u ^ b)))) {
    r = (((a >> (b & 31u)) - a) | ((1u ^ 3u) << ((y * z) & 31u)));
  } else {
    r = (((~z) | (x - z)) + (x % (((b | r) & 7u) + 1u)));
  }
  if ((x == 2147483647u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
