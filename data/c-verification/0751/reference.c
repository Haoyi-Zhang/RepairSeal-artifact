unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = y;
  unsigned b = (((~t) << ((a + 4294967295u) & 31u)) * (y >> ((t - t) & 31u)));
  unsigned r = 31u;
  if (((a & (t >> (b & 31u))) < (a / (((z - t) & 7u) + 1u)))) {
    r = (z - (3u / (((t % ((b & 7u) + 1u)) & 7u) + 1u)));
  } else {
    r = t;
  }
  if ((((y >> ((0u + t) & 31u)) < (r | (a | t))) && (!(y == z)))) {
    r = (((r ^ 31u) ^ (b | 3u)) | ((t - t) % (((r + y) & 7u) + 1u)));
  } else {
    r = (x & x);
  }
  return r;
}
