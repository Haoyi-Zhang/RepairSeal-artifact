unsigned f(unsigned x, unsigned y) {
  unsigned a = (2u * x);
  unsigned b = (((~y) + 3u) >> (((x << (4294967295u & 31u)) | a) & 31u));
  unsigned r = ((3u >> (y & 31u)) * (~(x ^ b)));
  if ((1u <= ((y * y) / (((y % ((y & 7u) + 1u)) & 7u) + 1u)))) {
    r = (3u - (x + (r / ((3u & 7u) + 1u))));
  } else {
    r = r;
  }
  if (((((x << (r & 31u)) & y) < (y >> (1u & 31u))) && ((((2147483647u << (r & 31u)) ^ y) < (~x)) || (((7u % ((2147483647u & 7u) + 1u)) >> ((r << (b & 31u)) & 31u)) == a)))) {
    r = (((r / ((a & 7u) + 1u)) << ((y << (b & 31u)) & 31u)) & 3u);
  } else {
    r = b;
  }
  return r;
}
