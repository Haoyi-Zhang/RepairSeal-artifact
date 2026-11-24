unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((1u | x) + (y - (x / ((y & 7u) + 1u))));
  unsigned b = 1u;
  unsigned r = 15u;
  if (((!(((y >> (a & 31u)) | (b << (y & 31u))) != ((r & x) << ((r * t) & 31u)))) && (z >= y))) {
    r = (2u << (((2147483647u - 4294967295u) - (1u ^ z)) & 31u));
  } else {
    r = (((2u & 31u) + 31u) % (((1u / (((r / ((t & 7u) + 1u)) & 7u) + 1u)) & 7u) + 1u));
  }
  if ((x == 3u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
