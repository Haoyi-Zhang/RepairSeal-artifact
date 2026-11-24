unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (((2147483647u * y) + (t >> (x & 31u))) & 15u);
  unsigned b = (((15u * x) >> (a & 31u)) - z);
  unsigned r = (a ^ ((a + x) + 7u));
  if ((((z ^ 2147483647u) << (3u & 31u)) == 3u)) {
    r = b;
  } else {
    r = (((3u / ((r & 7u) + 1u)) & (b + x)) % ((b & 7u) + 1u));
  }
  if ((((15u / ((b & 7u) + 1u)) / ((4294967295u & 7u) + 1u)) <= ((t - z) >> (4294967295u & 31u)))) {
    r = ((15u | (b + b)) << (b & 31u));
  } else {
    r = (((a >> (z & 31u)) | (x | r)) * (a * (x * r)));
  }
  if (((x == 3u) && (y == 2147483648u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
