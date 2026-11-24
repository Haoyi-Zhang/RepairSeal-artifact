unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((t | (x | 4294967295u)) << (z & 31u));
  unsigned b = y;
  unsigned r = ((a / (((z & z) & 7u) + 1u)) | (~(t << (y & 31u))));
  if (((x != 3u) || (x != 2u))) {
    r = x;
  } else {
    r = x;
  }
  return r;
}
