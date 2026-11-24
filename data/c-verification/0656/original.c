unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((t - x) + (t / ((z & 7u) + 1u))) | (1u % (((3u % ((y & 7u) + 1u)) & 7u) + 1u)));
  unsigned b = (((~a) - x) % (((y | z) & 7u) + 1u));
  unsigned r = a;
  if (((y * (y | 4294967295u)) > ((b >> (r & 31u)) * (x / ((y & 7u) + 1u))))) {
    r = (((r % ((z & 7u) + 1u)) >> ((a << (y & 31u)) & 31u)) | (2u & (x | a)));
  } else {
    r = ((~(~z)) ^ (r ^ (r | z)));
  }
  if ((a > (t | y))) {
    r = (((z | r) << ((z | y) & 31u)) / ((((t / ((31u & 7u) + 1u)) << ((b % ((z & 7u) + 1u)) & 31u)) & 7u) + 1u));
  } else {
    r = z;
  }
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
