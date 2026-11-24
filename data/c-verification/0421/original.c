unsigned f(unsigned x, unsigned y) {
  unsigned a = (((y * x) ^ (7u & y)) | ((~y) & (0u / ((x & 7u) + 1u))));
  unsigned b = (((y % ((y & 7u) + 1u)) / (((1u * 4294967295u) & 7u) + 1u)) | (2147483647u - (a | a)));
  unsigned r = (4294967295u - (b * (1u - 1u)));
  if (((a * b) == a)) {
    r = (((31u | x) % ((7u & 7u) + 1u)) % (((x & (y + r)) & 7u) + 1u));
  } else {
    r = b;
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
