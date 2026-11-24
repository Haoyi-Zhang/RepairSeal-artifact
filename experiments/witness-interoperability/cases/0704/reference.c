unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((t % ((x & 7u) + 1u)) >> (2u & 31u)) - ((z << (t & 31u)) >> (4294967295u & 31u)));
  unsigned b = (((a * a) - (t | y)) >> (a & 31u));
  unsigned r = (((z - t) >> ((t | b) & 31u)) | a);
  if ((b != 3u)) {
    r = r;
  } else {
    r = (15u & ((b / ((r & 7u) + 1u)) / ((x & 7u) + 1u)));
  }
  if ((((y | a) & (y * 15u)) == (x / ((y & 7u) + 1u)))) {
    r = (r ^ ((~z) * 4294967295u));
  } else {
    r = (((1u % ((b & 7u) + 1u)) | (15u % ((t & 7u) + 1u))) + 7u);
  }
  return r;
}
