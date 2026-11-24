unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((15u >> (2u & 31u)) | (1u + x)) | ((~31u) * (x * z)));
  unsigned b = (((t | a) << (y & 31u)) / ((y & 7u) + 1u));
  unsigned r = a;
  if ((x >= (4294967295u + (a ^ 2u)))) {
    r = b;
  } else {
    r = (~a);
  }
  if ((x == 3u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
