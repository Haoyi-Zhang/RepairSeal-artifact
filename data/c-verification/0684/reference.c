unsigned f(unsigned x, unsigned y) {
  unsigned a = (((x - y) % ((x & 7u) + 1u)) * (x - (2147483647u ^ x)));
  unsigned b = (~(y / (((~x) & 7u) + 1u)));
  unsigned r = (((a / ((a & 7u) + 1u)) % (((15u ^ 15u) & 7u) + 1u)) | y);
  if (((((b ^ x) % (((2u % ((7u & 7u) + 1u)) & 7u) + 1u)) == ((y + 4294967295u) / (((2147483647u >> (x & 31u)) & 7u) + 1u))) && (2147483647u < ((2u * a) ^ (~y))))) {
    r = (((2u + y) - (b % ((r & 7u) + 1u))) + ((0u % ((b & 7u) + 1u)) - r));
  } else {
    r = ((r * 4294967295u) << (r & 31u));
  }
  if ((((y | b) * (2u % ((2u & 7u) + 1u))) != b)) {
    r = y;
  } else {
    r = (((b % ((15u & 7u) + 1u)) ^ (x / ((31u & 7u) + 1u))) + b);
  }
  return r;
}
