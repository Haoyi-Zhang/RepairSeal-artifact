unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = 2u;
  unsigned b = (((z / ((4294967295u & 7u) + 1u)) | (y + y)) | ((a / ((a & 7u) + 1u)) | z));
  unsigned r = (((a * y) >> (y & 31u)) ^ 1u);
  if ((7u > b)) {
    r = ((15u * (a & r)) | (~(a >> (r & 31u))));
  } else {
    r = (z ^ (a & (31u ^ z)));
  }
  return r;
}
