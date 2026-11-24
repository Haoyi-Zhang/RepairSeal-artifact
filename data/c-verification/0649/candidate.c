unsigned f(unsigned x, unsigned y) {
  unsigned a = (2147483647u - x);
  unsigned b = 7u;
  unsigned r = (4294967295u >> (b & 31u));
  if ((((~a) * x) == ((r >> (0u & 31u)) * (a >> (y & 31u))))) {
    r = (((r % ((2u & 7u) + 1u)) | 15u) * a);
  } else {
    r = (((b / ((x & 7u) + 1u)) / (((a >> (b & 31u)) & 7u) + 1u)) % ((((x + a) % ((15u & 7u) + 1u)) & 7u) + 1u));
  }
  if (((r + (y ^ b)) > x)) {
    r = (((a / ((r & 7u) + 1u)) - (31u ^ y)) % (((a | (r >> (y & 31u))) & 7u) + 1u));
  } else {
    r = (((y / ((b & 7u) + 1u)) - x) | ((x >> (x & 31u)) & (b | 1u)));
  }
  if (((x == 2147483648u) && (y == 4294967295u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
